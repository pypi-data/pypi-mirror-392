import math
import logging

import torch
import torch.nn as nn
from torch.nn import functional as F

logger = logging.getLogger(__name__)
from SCMG.config import varables

# class ModelConfig():
#     rate_dropout_embedding = 0.1
#     rate_dropout_residue = 0.1
#     rate_dropout_attention = 0.1
#     block_size=125
#     def __init__(self, size_vocab, **kwargs):
#         self.size_vocab = size_vocab
#         for k,v in kwargs.items():
#             setattr(self, k, v)

class CausalSelfAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        assert config[varables.DIM_ATTENTION] % config[varables.NUM_HEADS] == 0
        self.key = nn.Linear(config[varables.DIM_EMBEDDING], config[varables.DIM_ATTENTION])
        self.query = nn.Linear(config[varables.DIM_EMBEDDING], config[varables.DIM_ATTENTION])
        self.value = nn.Linear(config[varables.DIM_EMBEDDING], config[varables.DIM_ATTENTION])
        self.dropout_attention = nn.Dropout(config[varables.RATE_DROPOUT])
        self.dropout_residue = nn.Dropout(config[varables.RATE_DROPOUT])
        self.projection = nn.Linear(config[varables.DIM_ATTENTION], config[varables.DIM_EMBEDDING])
        self.register_buffer("mask", torch.tril(torch.ones(config[varables.SIZE_BLOCK], config[varables.SIZE_BLOCK]))
                                     .view(1, 1, config[varables.SIZE_BLOCK], config[varables.SIZE_BLOCK]))
        self.n_head = config[varables.NUM_HEADS]
        self.single_head_dim = config[varables.DIM_ATTENTION] // self.n_head
        self.attention_features = config[varables.DIM_ATTENTION]

    def forward(self, x, layer_past=None):
        B, T, C = x.size()
        k =   self.key(x).view(B, T, self.n_head,self.single_head_dim).transpose(1, 2)
        q = self.query(x).view(B, T, self.n_head,self.single_head_dim).transpose(1, 2)
        v = self.value(x).view(B, T, self.n_head,self.single_head_dim).transpose(1, 2)
        att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))
        att = att.masked_fill(self.mask[:,:,:T,:T] == 0, float('-inf'))
        att = F.softmax(att, dim=-1)
        att = self.dropout_attention(att)
        y = att @ v
        y = y.transpose(1, 2).contiguous().view(B, T, self.attention_features)
        y = self.dropout_residue(self.projection(y))
        return y


class CrossAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        assert config[varables.DIM_ATTENTION] % config[varables.NUM_HEADS] == 0
        self.key = nn.Linear(config[varables.DIM_EMBEDDING], config[varables.DIM_ATTENTION])
        self.query = nn.Linear(config[varables.DIM_EMBEDDING], config[varables.DIM_ATTENTION])
        self.value = nn.Linear(config[varables.DIM_EMBEDDING], config[varables.DIM_ATTENTION])
        self.dropout_attention = nn.Dropout(config[varables.RATE_DROPOUT])
        self.dropout_residue = nn.Dropout(config[varables.RATE_DROPOUT])
        self.projection = nn.Linear(config[varables.DIM_ATTENTION], config[varables.DIM_EMBEDDING])
        self.n_head = config[varables.NUM_HEADS]
        self.single_head_dim = config[varables.DIM_ATTENTION] // self.n_head
        self.attention_features = config[varables.DIM_ATTENTION]
        self.register_buffer("mask", torch.tril(torch.ones(config[varables.SIZE_BLOCK], config[varables.SIZE_BLOCK]))
                                .view(1, 1, config[varables.SIZE_BLOCK], config[varables.SIZE_BLOCK]))

    def forward(self, x_encoder,x_decoder, layer_past=None):
        B_encoder, T_encoder, C_encoder = x_encoder.size()
        B_decoder, T_decoder, C_decoder = x_decoder.size()
        k = self.key(  x_encoder).view(B_encoder, T_encoder, self.n_head,self.single_head_dim).transpose(1, 2)
        q = self.query(x_decoder).view(B_encoder, T_decoder, self.n_head,self.single_head_dim).transpose(1, 2)
        v = self.value(x_encoder).view(B_encoder, T_encoder, self.n_head,self.single_head_dim).transpose(1, 2)
        att = (q @ k.transpose(-2, -1)) * (1.0 / math.sqrt(k.size(-1)))
        att = att.masked_fill(self.mask[:,:,:T_decoder,:T_encoder] == 0, float('-inf'))
        att = F.softmax(att, dim=-1)
        att = self.dropout_attention(att)
        y = att @ v
        y = y.transpose(1, 2).contiguous().view(B_encoder, T_decoder, self.attention_features)
        y = self.dropout_residue(self.projection(y))
        return y




class EncoderBlock(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.ln1 = nn.LayerNorm(config[varables.DIM_EMBEDDING])
        self.ln2 = nn.LayerNorm(config[varables.DIM_EMBEDDING])
        self.attn = CausalSelfAttention(config)
        self.mlp = nn.Sequential(
            nn.Linear(config[varables.DIM_EMBEDDING], config[varables.DIM_FEEDFORWARD]),
            nn.GELU(),
            nn.Linear(config[varables.DIM_FEEDFORWARD], config[varables.DIM_EMBEDDING]),
            nn.Dropout(config[varables.RATE_DROPOUT]),
        )

    def forward(self, x):
         # = y_input
        x = x + self.attn(self.ln1(x))
        x = x + self.mlp(self.ln2(x))
        return x

class DecoderBlock(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.ln1 = nn.LayerNorm(config[varables.DIM_EMBEDDING])
        self.ln2 = nn.LayerNorm(config[varables.DIM_EMBEDDING])
        self.masked_attn = CausalSelfAttention(config)
        self.cross_attn = CrossAttention(config)
        self.mlp = nn.Sequential(
            nn.Linear(config[varables.DIM_EMBEDDING], config[varables.DIM_FEEDFORWARD]),
            nn.GELU(),
            nn.Linear(config[varables.DIM_FEEDFORWARD], config[varables.DIM_EMBEDDING]),
            nn.Dropout(config[varables.RATE_DROPOUT]),
        )

    def forward(self, x_encoder,x):
         # = y_input
        x = x + self.masked_attn(self.ln1(x))
        x = x + self.cross_attn(x_encoder,self.ln1(x))
        x = x + self.mlp(self.ln2(x))
        return x

















import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class Norm(nn.Module):
    def __init__(self, d_model, eps = 1e-6):
        super().__init__()
    
        self.size = d_model
        
        # create two learnable parameters to calibrate normalisation
        self.alpha = nn.Parameter(torch.ones(self.size))
        self.bias = nn.Parameter(torch.zeros(self.size))
        
        self.eps = eps
    
    def forward(self, x):
        norm = self.alpha * (x - x.mean(dim=-1, keepdim=True)) \
        / (x.std(dim=-1, keepdim=True) + self.eps) + self.bias
        return norm

def attention(q, k, v, d_k, mask=None, dropout=None):
    
    scores = torch.matmul(q, k.transpose(-2, -1)) /  math.sqrt(d_k)
    
    if mask is not None:
        mask = mask.unsqueeze(1)
        scores = scores.masked_fill(mask == 0, -1e9)
    
    scores = F.softmax(scores, dim=-1)
    
    if dropout is not None:
        scores = dropout(scores)
        
    output = torch.matmul(scores, v)
    return output

class MultiHeadAttention(nn.Module):
    def __init__(self, heads, d_model, dropout = 0.1):
        super().__init__()
        
        self.d_model = d_model
        self.d_k = d_model // heads
        self.h = heads
        
        self.q_linear = nn.Linear(d_model, d_model)
        self.v_linear = nn.Linear(d_model, d_model)
        self.k_linear = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
        self.out = nn.Linear(d_model, d_model)
    
    def forward(self, q, k, v, mask=None):
        
        bs = q.size(0)
        
        # perform linear operation and split into N heads
        k = self.k_linear(k).view(bs, -1, self.h, self.d_k)
        q = self.q_linear(q).view(bs, -1, self.h, self.d_k)
        v = self.v_linear(v).view(bs, -1, self.h, self.d_k)
        
        # transpose to get dimensions bs * N * sl * d_model
        k = k.transpose(1,2)
        q = q.transpose(1,2)
        v = v.transpose(1,2)
        

        # calculate attention using function we will define next
        scores = attention(q, k, v, self.d_k, mask, self.dropout)
        # concatenate heads and put through final linear layer
        concat = scores.transpose(1,2).contiguous()\
        .view(bs, -1, self.d_model)
        output = self.out(concat)
    
        return output

class FeedForward(nn.Module):
    def __init__(self, d_model, d_ff=2048, dropout = 0.1):
        super().__init__() 
    
        # We set d_ff as a default to 2048
        self.linear_1 = nn.Linear(d_model, d_ff)
        self.dropout = nn.Dropout(dropout)
        self.linear_2 = nn.Linear(d_ff, d_model)
    
    def forward(self, x):
        x = self.dropout(F.relu(self.linear_1(x)))
        x = self.linear_2(x)
        return x




import torch
import torch.nn as nn 
import copy


class EncoderLayer(nn.Module):
    def __init__(self, d_model, heads, dropout=0.1):
        super().__init__()
        self.norm_1 = Norm(d_model)
        self.norm_2 = Norm(d_model)
        self.attn = MultiHeadAttention(heads, d_model, dropout=dropout)
        self.ff = FeedForward(d_model, dropout=dropout)
        self.dropout_1 = nn.Dropout(dropout)
        self.dropout_2 = nn.Dropout(dropout)
        
    def forward(self, x, mask):
        x2 = self.norm_1(x)
        x = x + self.dropout_1(self.attn(x2,x2,x2,mask))
        x2 = self.norm_2(x)
        x = x + self.dropout_2(self.ff(x2))
        return x
    
# build a decoder layer with two multi-head attention layers and
# one feed-forward layer
class DecoderLayer(nn.Module):
    def __init__(self, d_model, heads, dropout=0.1):
        super().__init__()
        self.norm_1 = Norm(d_model)
        self.norm_2 = Norm(d_model)
        self.norm_3 = Norm(d_model)
        
        self.dropout_1 = nn.Dropout(dropout)
        self.dropout_2 = nn.Dropout(dropout)
        self.dropout_3 = nn.Dropout(dropout)
        
        self.attn_1 = MultiHeadAttention(heads, d_model, dropout=dropout)
        self.attn_2 = MultiHeadAttention(heads, d_model, dropout=dropout)
        self.ff = FeedForward(d_model, dropout=dropout)

    def forward(self, x, e_outputs, src_mask, trg_mask):
        x2 = self.norm_1(x)
        x = x + self.dropout_1(self.attn_1(x2, x2, x2, trg_mask))
        x2 = self.norm_2(x)
        x = x + self.dropout_2(self.attn_2(x2, e_outputs, e_outputs, \
        src_mask))
        x2 = self.norm_3(x)
        x = x + self.dropout_3(self.ff(x2))
        return x


import torch
import torch.nn as nn
import math
from torch.autograd import Variable

class Embedder(nn.Module):
    def __init__(self, vocab_size, d_model):
        super().__init__()
        self.d_model = d_model
        self.embed = nn.Embedding(vocab_size, d_model)
    def forward(self, x):
        return self.embed(x)

class PositionalEncoder(nn.Module):
    def __init__(self, d_model, max_seq_len = 200, dropout = 0.1):
        super().__init__()
        self.d_model = d_model
        self.dropout = nn.Dropout(dropout)
        # create constant 'pe' matrix with values dependant on 
        # pos and i
        pe = torch.zeros(max_seq_len, d_model)
        for pos in range(max_seq_len):
            for i in range(0, d_model, 2):
                pe[pos, i] = \
                math.sin(pos / (10000 ** ((2 * i)/d_model)))
                pe[pos, i + 1] = \
                math.cos(pos / (10000 ** ((2 * (i + 1))/d_model)))
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)
 
    
    def forward(self, x):
        # make embeddings relatively larger
        x = x * math.sqrt(self.d_model)
        #add constant to embedding
        seq_len = x.size(1)
        pe = Variable(self.pe[:,:seq_len], requires_grad=False)
        if x.is_cuda:
            pe.cuda()
        x = x + pe
        return self.dropout(x)

def get_clones(module, N):
    return nn.ModuleList([copy.deepcopy(module) for i in range(N)])

class Encoder(nn.Module):
    def __init__(self, vocab_size, d_model, N, heads, dropout):
        super().__init__()
        self.N = N
        self.embed = Embedder(vocab_size, d_model)
        self.pe = PositionalEncoder(d_model, dropout=dropout)
        self.layers = get_clones(EncoderLayer(d_model, heads, dropout), N)
        self.norm = Norm(d_model)
    def forward(self, src, mask):
        x = self.embed(src)
        x = self.pe(x)
        for i in range(self.N):
            x = self.layers[i](x, mask)
        return self.norm(x)
    
class Decoder(nn.Module):
    def __init__(self, vocab_size, d_model, N, heads, dropout):
        super().__init__()
        self.N = N
        self.embed = Embedder(vocab_size, d_model)
        self.pe = PositionalEncoder(d_model, dropout=dropout)
        self.layers = get_clones(DecoderLayer(d_model, heads, dropout), N)
        self.norm = Norm(d_model)
    def forward(self, trg, e_outputs, src_mask, trg_mask):
        x = self.embed(trg)
        x = self.pe(x)
        for i in range(self.N):
            x = self.layers[i](x, e_outputs, src_mask, trg_mask)
        return self.norm(x)

class Model(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.encoder = Encoder(len(config["vocab_encoder"]), config[varables.DIM_ATTENTION], config[varables.NUM_LAYERS], config[varables.NUM_HEADS], config[varables.RATE_DROPOUT])
        self.decoder = Decoder(len(config["vocab_decoder"]), config[varables.DIM_ATTENTION], config[varables.NUM_LAYERS], config[varables.NUM_HEADS], config[varables.RATE_DROPOUT])
        self.out = nn.Linear(config[varables.DIM_ATTENTION], len(config["vocab_decoder"]))
        # self.tok_emb = nn.Embedding(config[varables.SIZE_VOCAB], config[varables.DIM_EMBEDDING])
        # self.pos_emb = nn.Parameter(torch.zeros(1, config[varables.SIZE_BLOCK], config[varables.DIM_EMBEDDING]))
        # self.drop = nn.Dropout(config[varables.RATE_DROPOUT])
        # self.encoder_blocks = nn.ModuleList([EncoderBlock(config) for _ in range(config[varables.NUM_LAYERS])])
        # self.decoder_blocks = nn.ModuleList([DecoderBlock(config) for _ in range(config[varables.NUM_LAYERS])])
        # self.blocks = nn.Sequential(*[DecoderBlock(config) for _ in range(config[varables.NUM_LAYERS])])
        # self.ln_f = nn.LayerNorm(config[varables.DIM_EMBEDDING])
        # self.head = nn.Linear(config[varables.DIM_EMBEDDING], config[varables.SIZE_VOCAB], bias=False)
        # self.block_size = config[varables.SIZE_BLOCK]
        # self.apply(self._init_weights)
        # logger.info("number of parameters: %e", sum(p.numel() for p in self.parameters()))
        self.optimizer = None

    def get_block_size(self):
        return self.block_size

    def _init_weights(self, module):
        if isinstance(module, (nn.Linear, nn.Embedding)):
            module.weight.data.normal_(mean=0.0, std=0.02)
            if isinstance(module, nn.Linear) and module.bias is not None:
                module.bias.data.zero_()
        elif isinstance(module, nn.LayerNorm):
            module.bias.data.zero_()
            module.weight.data.fill_(1.0)
    def init_optimizers(self,train_config):
        optimizer = torch.optim.Adam(self.parameters(), lr=train_config[varables.RATE_LEARNING])
        return optimizer
    def init_scheduler(self,train_config):
        scheduler = torch.optim.lr_scheduler.StepLR(self.optimizer, step_size=train_config[varables.SIZE_STEP], gamma=train_config[varables.GAMMA])
        return scheduler
    def get_collate_fn(self, vocab_encoder,vocab_decoder):
        def collate(results):
            x_in = [a[0] for a in results]
            y_in = [a[1] for a in results]
            boundary = -1
            max_len_x = max([len(a) for a in x_in])
            max_len_y = max([len(a) for a in y_in])
            x = torch.tensor([(a+[vocab_encoder[varables.TOKEN_PAD]]*(max_len_x-len(a))) for a in x_in],dtype=torch.long)
            y = torch.tensor([(a+[vocab_decoder[varables.TOKEN_PAD]]*(max_len_y-len(a))) for a in y_in],dtype=torch.long)
            return x,y,boundary
        return collate
    def forward(self, src, trg, trg_out, boundary=None):
        src_mask = None
        trg_mask = torch.tril(torch.ones(trg.shape[1], trg.shape[1])).view(1, 1, trg.shape[1], trg.shape[1]).to(trg.device)
        e_outputs = self.encoder(src, src_mask)
        d_output = self.decoder(trg, e_outputs, src_mask, trg_mask)
        logits = self.out(d_output)
        loss = None
        if trg_out is not None:
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), trg_out.view(-1))
        return logits, loss

# mark test