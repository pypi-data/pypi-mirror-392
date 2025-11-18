import math
import logging

import torch
import torch.nn as nn
from torch.nn import functional as F

# logger = logging.getLogger(__name__)
from SCMG.config import varables
from torch.autograd import Variable

# class PositionalEncoder(nn.Module):
#     def __init__(self, config):
#         super().__init__()
#         pe = torch.zeros(config[varables.SIZE_BLOCK], config[varables.DIM_ATTENTION])
#         for pos in range(config[varables.SIZE_BLOCK]):
#             for i in range(0, config[varables.DIM_ATTENTION], 2):
#                 pe[pos, i] = \
#                 math.sin(pos / (10000 ** ((2 * i)/config[varables.DIM_ATTENTION])))
#                 pe[pos, i + 1] = \
#                 math.cos(pos / (10000 ** ((2 * (i + 1))/config[varables.DIM_ATTENTION])))                
#         pe = pe.unsqueeze(0)
#         self.register_buffer('pe', pe)
#     def forward(self, T):
#         #add constant to embedding
#         x = Variable(self.pe[:,:T], requires_grad=False)
#         return x



class PositionalEncoder(nn.Module):
    def __init__(self, config):
        super(PositionalEncoder, self).__init__()
        self.Dropout = nn.Dropout(p=config[varables.RATE_DROPOUT])
        max_len = config[varables.SIZE_BLOCK]
        pe = torch.zeros(max_len, config[varables.DIM_ATTENTION])
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, config[varables.DIM_ATTENTION], 2).float() * (-math.log(10000.0) / config[varables.DIM_ATTENTION]))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)
    def forward(self, T):
        x = self.Dropout(self.pe[:,:T, :])
        return x



class Attention(nn.Module):
    def __init__(self, config):
        super().__init__()
        assert config[varables.DIM_ATTENTION] % config[varables.NUM_HEADS] == 0
        self.Key = nn.Linear(config[varables.DIM_EMBEDDING], config[varables.DIM_ATTENTION])
        self.Query = nn.Linear(config[varables.DIM_EMBEDDING], config[varables.DIM_ATTENTION])
        self.Value = nn.Linear(config[varables.DIM_EMBEDDING], config[varables.DIM_ATTENTION])
        self.Dropout_Attention = nn.Dropout(config[varables.RATE_DROPOUT])
        self.Dropout_Residue = nn.Dropout(config[varables.RATE_DROPOUT])
        self.Projection = nn.Linear(config[varables.DIM_ATTENTION], config[varables.DIM_EMBEDDING])
        self.NumberOfHeads = config[varables.NUM_HEADS]
        self.DimHead = config[varables.DIM_ATTENTION] // self.NumberOfHeads
        self.DimAttention = config[varables.DIM_ATTENTION]

    def forward(self, X_1,X_2, mask=None):
        if X_2 is None:
            X_2 = X_1
        BatchSize, T_Encoder, _ = X_1.size()
        BatchSize, T_Decoder, _ = X_2.size()
        K = self.Key(  X_1).view(BatchSize, T_Encoder, self.NumberOfHeads,self.DimHead).transpose(1, 2)
        Q = self.Query(X_2).view(BatchSize, T_Decoder, self.NumberOfHeads,self.DimHead).transpose(1, 2)
        V = self.Value(X_1).view(BatchSize, T_Encoder, self.NumberOfHeads,self.DimHead).transpose(1, 2)
        # k,q,v dimension: (BatchSize, SequenceSize, NumberOfHeads, HeadDimension) 3,4,5,16
        ScoreAttention = (Q @ K.transpose(-2, -1)) / math.sqrt(self.DimHead)
        ScoreAttention = ScoreAttention.masked_fill(mask==0, -1e9)
        ScoreAttention = F.softmax(ScoreAttention, dim=-1)
        ScoreAttention = self.Dropout_Attention(ScoreAttention)
        # k.transpose(-2,-1): 3,4,16,5
        # (q@(k.transpose(-2,-1))): 3,4,5,5
        Z = ScoreAttention @ V
        # y dimension: 3,4,5,16
        Z = Z.transpose(1, 2).contiguous().view(BatchSize, T_Decoder, self.DimAttention)
        # y dimension: 3,5,64
        Z = self.Dropout_Residue(self.Projection(Z))
        return Z










class FeedForward(nn.Module):
    def __init__(self, config):
        super().__init__()
        if config[varables.DIM_FEEDFORWARD] == 0:
            Dim_FeedForward = config[varables.DIM_ATTENTION] *4
        else:
            Dim_FeedForward = config[varables.DIM_FEEDFORWARD]
        self.Linear1 = nn.Linear(config[varables.DIM_EMBEDDING], Dim_FeedForward)
        self.GELU = nn.GELU()
        self.Linear2 = nn.Linear(Dim_FeedForward, config[varables.DIM_EMBEDDING])
        self.Dropout = nn.Dropout(config[varables.RATE_DROPOUT])

    def forward(self,x):
        x = self.Linear1(x)
        x = self.GELU   (x)
        x = self.Dropout(x)
        x = self.Linear2(x)
        return x

class DecoderBlock(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.LayerNorm1      = nn.LayerNorm(config[varables.DIM_EMBEDDING])
        self.LayerNorm2      = nn.LayerNorm(config[varables.DIM_EMBEDDING])
        self.LayerNorm3      = nn.LayerNorm(config[varables.DIM_EMBEDDING])
        self.Dropout1 = nn.Dropout(config[varables.RATE_DROPOUT])
        self.Dropout2 = nn.Dropout(config[varables.RATE_DROPOUT])
        self.Dropout3 = nn.Dropout(config[varables.RATE_DROPOUT])
        self.AttentionMasked = Attention(  config)
        self.AttentionCross  = Attention(  config)
        self.FeedForward     = FeedForward(config)

    def forward(self, X_Encoder,X_Decoder,Mask_Cross,Mask_Decoder):
        X_Decoder = self.Dropout1(X_Decoder + self.AttentionMasked(self.LayerNorm1(X_Decoder), None,                       Mask_Decoder))
        X_Decoder = self.Dropout2(X_Decoder + self.AttentionCross (                X_Encoder,  self.LayerNorm2(X_Decoder), Mask_Cross  ))
        X_Decoder = self.Dropout3(X_Decoder + self.FeedForward    (self.LayerNorm3(X_Decoder)                                          ))
        return X_Decoder



















class Model(nn.Module):
    def __init__(self, config):
        super().__init__()
        # Varables
        self.Dim_Attention = config[varables.DIM_ATTENTION]
        self.Token_Padding_Encoder = config["Token_Padding_Encoder"]
        self.Token_Padding_Decoder = config["Token_Padding_Decoder"]
        # Embedding and positional encoding layers
        self.Embedding_Encoder = nn.Embedding(len(config["vocab_encoder"]), config[varables.DIM_ATTENTION])
        self.Embedding_Decoder = nn.Embedding(len(config["vocab_decoder"]), config[varables.DIM_ATTENTION])
        self.pos_emb = PositionalEncoder(config)
        # Dropout and normalization layers
        self.Dropout1 = nn.Dropout(config[varables.RATE_DROPOUT])
        self.Dropout2 = nn.Dropout(config[varables.RATE_DROPOUT])
        self.LayerNorm1 = nn.LayerNorm(config[varables.DIM_EMBEDDING])
        self.LayerNorm2 = nn.LayerNorm(config[varables.DIM_EMBEDDING])
        # Transformer layers
        self.encoder_blocks = nn.ModuleList([EncoderBlock(config) for _ in range(config[varables.NUM_LAYERS])])
        self.decoder_blocks = nn.ModuleList([DecoderBlock(config) for _ in range(config[varables.NUM_LAYERS])])
        # Output layer
        self.head = nn.Linear(config[varables.DIM_ATTENTION], len(config["vocab_decoder"]), bias=False)
        # Init
        self.apply(self._init_weights)
        self.optimizer = None
        # logger.info("number of parameters: %e", sum(p.numel() for p in self.parameters()))

    def _init_weights(self, module):
        for p in module.parameters():
            if p.dim() > 1:
                nn.init.xavier_uniform_(p)
        # if isinstance(module, (nn.Linear, nn.Embedding)):
        #     module.weight.data.normal_(mean=0.0, std=0.02)
        #     if isinstance(module, nn.Linear) and module.bias is not None:
        #         module.bias.data.zero_()
        # elif isinstance(module, nn.LayerNorm):
        #     module.bias.data.zero_()
        #     module.weight.data.fill_(1.0)
    def init_optimizers(self,train_config):
        optimizer = torch.optim.Adam(self.parameters(), lr=train_config[varables.RATE_LEARNING])
        return optimizer
    def init_scheduler(self,train_config):
        scheduler = torch.optim.lr_scheduler.StepLR(self.optimizer, step_size=train_config[varables.SIZE_STEP], gamma=train_config[varables.GAMMA])
        return scheduler
    def get_collate_fn(self, vocab_encoder,vocab_decoder):
        def collate(results):
            X_Encoder = [a[0] for a in results]
            X_Decoder = [a[1] for a in results]
            boundary = -1
            max_len_x = max([len(a) for a in X_Encoder])
            max_len_y = max([len(a) for a in X_Decoder])
            x = torch.tensor([(a+[vocab_encoder[varables.TOKEN_PAD]]*(max_len_x-len(a))) for a in X_Encoder],dtype=torch.long)
            y = torch.tensor([(a+[vocab_decoder[varables.TOKEN_PAD]]*(max_len_y-len(a))) for a in X_Decoder],dtype=torch.long)
            return x,y,boundary
        return collate

    def generate_masks(self,X_Encoder, X_Decoder):
        # Generate encoder, decoder, cross masks
        BatchSize, T_Encoder, _ = X_Encoder.size()
        BatchSize, T_Decoder, _ = X_Decoder.size()
        X = torch.cat([X_Encoder,torch.tensor([self.Token_Sep_Encoder],device=X_Encoder.device).unsqueeze(0).repeat(BatchSize,1),X_Decoder],axis=1)
        CutIndex=T_Encoder+1
        # T = X_Decoder.shape[1]
        Mask_Encoder = (X_Encoder != self.Token_Padding_Encoder).unsqueeze(-2).unsqueeze(-2)
        Mask_Decoder = (X_Decoder != self.Token_Padding_Decoder).unsqueeze(-2).unsqueeze(-2).repeat(1,1,T,1)
        Mask_Cross   = (X_Encoder != self.Token_Padding_Encoder).unsqueeze(-2).unsqueeze(-2)
        mask_tril = torch.tril(torch.ones(T, T)).view(1, 1, T, T).to(Mask_Decoder.device)
        Mask_Decoder = Mask_Decoder.masked_fill(mask_tril==0,0)
        return Mask_Encoder,Mask_Decoder,Mask_Cross

    def forward(self, X_Encoder, X_Decoder, Y_Decoder_Ref=None,boundary=None):
        Mask_Decoder,Mask_UTFMG,CutIndex = self.generate_masks(X_Encoder, X_Decoder)
        # preprocess
        X_Decoder = self.Dropout2(self.Embedding_Decoder(X_Decoder) * math.sqrt(self.Dim_Attention) + self.pos_emb(X_Decoder.size(1)))
        #### Now X_Encoder: BatchSize, SequenceLength, DimAttention         
        # Decoder blocks
        for decoder_block in self.decoder_blocks:
            X_Decoder = decoder_block(X_Encoder,X_Decoder,Mask_UTFMG)
        X_Decoder = self.LayerNorm2(X_Decoder)
        Y_Decoder_Logits = self.head(X_Decoder[:,CutIndex:])
        loss = None
        if Y_Decoder_Ref is not None:
            loss = F.cross_entropy(Y_Decoder_Logits.view(-1, Y_Decoder_Logits.size(-1)), Y_Decoder_Ref.view(-1),ignore_index=self.Token_Padding_Decoder)
        return Y_Decoder_Logits, loss

    # def generate_masks(self,X_Encoder, X_Decoder):
    #     # Generate encoder, decoder, cross masks
    #     Mask_Encoder = (X_Encoder != self.Token_Padding_Encoder).unsqueeze(-2).int().cpu()
    #     Mask_Decoder = (X_Decoder != self.Token_Padding_Decoder).unsqueeze(-2).int().cpu()
    #     Mask_Cross   = Mask_Decoder.unsqueeze(-1) @ Mask_Encoder.unsqueeze(-2)
    #     Mask_Encoder = Mask_Encoder.unsqueeze(-1) @ Mask_Encoder.unsqueeze(-2)
    #     Mask_Decoder = Mask_Decoder.unsqueeze(-1) @ Mask_Decoder.unsqueeze(-2)
    #     T = X_Decoder.shape[1]
    #     mask_tril = torch.tril(torch.ones(T, T)).view(1, 1, T, T)
    #     Mask_Decoder = Mask_Decoder.masked_fill(mask_tril==0,0)
    #     Mask_Encoder = Mask_Encoder.to(X_Encoder.device)
    #     Mask_Decoder = Mask_Decoder.to(X_Decoder.device)
    #     Mask_Cross = Mask_Cross.to(X_Encoder.device)
    #     return Mask_Encoder,Mask_Decoder,Mask_Cross
