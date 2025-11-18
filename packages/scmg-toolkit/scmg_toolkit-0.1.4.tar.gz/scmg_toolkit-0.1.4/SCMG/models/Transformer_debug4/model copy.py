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

class Model(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.tok_emb = nn.Embedding(config[varables.SIZE_VOCAB], config[varables.DIM_EMBEDDING])
        self.pos_emb = nn.Parameter(torch.zeros(1, config[varables.SIZE_BLOCK], config[varables.DIM_EMBEDDING]))
        self.drop = nn.Dropout(config[varables.RATE_DROPOUT])
        self.encoder_blocks = nn.ModuleList([EncoderBlock(config) for _ in range(config[varables.NUM_LAYERS])])
        self.decoder_blocks = nn.ModuleList([DecoderBlock(config) for _ in range(config[varables.NUM_LAYERS])])
        # self.blocks = nn.Sequential(*[DecoderBlock(config) for _ in range(config[varables.NUM_LAYERS])])
        self.ln_f = nn.LayerNorm(config[varables.DIM_EMBEDDING])
        self.head = nn.Linear(config[varables.DIM_EMBEDDING], config[varables.SIZE_VOCAB], bias=False)
        self.block_size = config[varables.SIZE_BLOCK]
        self.apply(self._init_weights)
        logger.info("number of parameters: %e", sum(p.numel() for p in self.parameters()))
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
    def get_collate_fn(self, vocab):
        def collate(results):
            x_in = [a[0] for a in results]
            y_in = [a[1] for a in results]
            boundary = -1
            max_len_x = max([len(a) for a in x_in])
            max_len_y = max([len(a) for a in y_in])
            x = torch.tensor([(a+[vocab[varables.TOKEN_PAD]]*(max_len_x-len(a))) for a in x_in],dtype=torch.long)
            y = torch.tensor([(a+[vocab[varables.TOKEN_PAD]]*(max_len_y-len(a))) for a in y_in],dtype=torch.long)
            return x,y,boundary
        return collate

    def forward(self, x_in, y_in, y_out=None,boundary=None):
        x_in = self.drop(self.tok_emb(x_in) + self.pos_emb[:, :x_in.size()[1], :])
        y_in = self.drop(self.tok_emb(y_in) + self.pos_emb[:, :y_in.size()[1], :])        
        #
        for encoder_block in self.encoder_blocks:
            x_in = encoder_block(x_in)
        x_in = self.ln_f(x_in)
        for decoder_block in self.decoder_blocks:
            y_in = decoder_block(x_in,y_in)
        y_in = self.ln_f(y_in)        
        logits = self.head(y_in)
        loss = None
        if y_out is not None:
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), y_out.view(-1))
        return logits, loss

# mark test