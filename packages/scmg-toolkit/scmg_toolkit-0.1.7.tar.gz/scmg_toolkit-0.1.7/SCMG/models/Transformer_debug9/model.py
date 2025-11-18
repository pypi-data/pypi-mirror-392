import math
import logging

import torch
import torch.nn as nn
from torch.nn import functional as F
import partialsmiles as ps
# logger = logging.getLogger(__name__)
from SCMG.config import varables as VBS
from torch.autograd import Variable
import partialsmiles as ps
from SCMG.utils.utils_rsd import *
from rdkit import Chem
from rdkit import RDLogger 
RDLogger.DisableLog('rdApp.*')

class PositionalEncoder(nn.Module):
    def __init__(self, config):
        super(PositionalEncoder, self).__init__()
        self.Dropout = nn.Dropout(p=config[VBS.RATE_DROPOUT])
        max_len = config[VBS.SIZE_BLOCK]
        pe = torch.zeros(max_len, config[VBS.DIM_EMBEDDING])
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, config[VBS.DIM_EMBEDDING], 2).float() * (-math.log(10000.0) / config[VBS.DIM_EMBEDDING]))
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
        assert config[VBS.DIM_ATTENTION] % config[VBS.NUM_HEADS] == 0
        self.Key = nn.Linear(config[VBS.DIM_EMBEDDING], config[VBS.DIM_ATTENTION])
        self.Query = nn.Linear(config[VBS.DIM_EMBEDDING], config[VBS.DIM_ATTENTION])
        self.Value = nn.Linear(config[VBS.DIM_EMBEDDING], config[VBS.DIM_ATTENTION])
        self.Dropout_Attention = nn.Dropout(config[VBS.RATE_DROPOUT])
        self.Dropout_Residue = nn.Dropout(config[VBS.RATE_DROPOUT])
        self.Projection = nn.Linear(config[VBS.DIM_ATTENTION], config[VBS.DIM_EMBEDDING])
        self.NumberOfHeads = config[VBS.NUM_HEADS]
        self.DimHead = config[VBS.DIM_ATTENTION] // self.NumberOfHeads
        self.DimAttention = config[VBS.DIM_ATTENTION]

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
        if config[VBS.DIM_FEEDFORWARD] == 0:
            Dim_FeedForward = config[VBS.DIM_ATTENTION] *4
        else:
            Dim_FeedForward = config[VBS.DIM_FEEDFORWARD]
        self.Linear1 = nn.Linear(config[VBS.DIM_EMBEDDING], Dim_FeedForward)
        self.GELU = nn.GELU()
        self.Linear2 = nn.Linear(Dim_FeedForward, config[VBS.DIM_EMBEDDING])
        self.Dropout = nn.Dropout(config[VBS.RATE_DROPOUT])

    def forward(self,x):
        x = self.Linear1(x)
        x = self.GELU   (x)
        x = self.Dropout(x)
        x = self.Linear2(x)
        return x




class EncoderBlock(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.LayerNorm1      = nn.LayerNorm(config[VBS.DIM_EMBEDDING])
        self.LayerNorm2      = nn.LayerNorm(config[VBS.DIM_EMBEDDING])
        self.Dropout1 = nn.Dropout(config[VBS.RATE_DROPOUT])
        self.Dropout2 = nn.Dropout(config[VBS.RATE_DROPOUT])
        self.Attention       = Attention(  config)
        self.FeedForward     = FeedForward(config)

    def forward(self, X_Encoder,Mask_Encoder):
        X_Encoder = self.LayerNorm1(X_Encoder + self.Attention  (self.Dropout1(X_Encoder), None, Mask_Encoder))
        X_Encoder = self.LayerNorm2(X_Encoder + self.FeedForward(self.Dropout2(X_Encoder)))
        return X_Encoder

class DecoderBlock(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.LayerNorm1      = nn.LayerNorm(config[VBS.DIM_EMBEDDING])
        self.LayerNorm2      = nn.LayerNorm(config[VBS.DIM_EMBEDDING])
        self.LayerNorm3      = nn.LayerNorm(config[VBS.DIM_EMBEDDING])
        self.Dropout1 = nn.Dropout(config[VBS.RATE_DROPOUT])
        self.Dropout2 = nn.Dropout(config[VBS.RATE_DROPOUT])
        self.Dropout3 = nn.Dropout(config[VBS.RATE_DROPOUT])
        self.AttentionMasked = Attention(  config)
        self.AttentionCross  = Attention(  config)
        self.FeedForward     = FeedForward(config)

    def forward(self, X_Encoder,X_Decoder,Mask_Cross,Mask_Decoder):
        X_Decoder = self.LayerNorm1(X_Decoder + self.AttentionMasked(self.Dropout1(X_Decoder), None,                       Mask_Decoder))
        X_Decoder = self.LayerNorm2(X_Decoder + self.AttentionCross (                X_Encoder,  self.Dropout2(X_Decoder), Mask_Cross  ))
        X_Decoder = self.LayerNorm3(X_Decoder + self.FeedForward    (self.Dropout3(X_Decoder)                                          ))
        return X_Decoder





class Model(nn.Module):
    def __init__(self, config):
        super().__init__()
        # VBS
        self.Dim_Embedding = config[VBS.DIM_EMBEDDING]
        self.Token_Padding_Encoder = config["Token_Padding_Encoder"]
        self.Token_Padding_Decoder = config["Token_Padding_Decoder"]
        # Embedding and positional encoding layers
        self.Embedding_Encoder = nn.Embedding(len(config["vocab_encoder"]), config[VBS.DIM_EMBEDDING])
        self.Embedding_Decoder = nn.Embedding(len(config["vocab_decoder"]), config[VBS.DIM_EMBEDDING])
        self.pos_emb = PositionalEncoder(config)
        # Dropout and normalization layers
        self.Dropout1 = nn.Dropout(config[VBS.RATE_DROPOUT])
        self.Dropout2 = nn.Dropout(config[VBS.RATE_DROPOUT])
        self.LayerNorm1 = nn.LayerNorm(config[VBS.DIM_EMBEDDING])
        self.LayerNorm2 = nn.LayerNorm(config[VBS.DIM_EMBEDDING])
        # Transformer layers
        self.encoder_blocks = nn.ModuleList([EncoderBlock(config) for _ in range(config[VBS.NUM_LAYERS])])
        self.decoder_blocks = nn.ModuleList([DecoderBlock(config) for _ in range(config[VBS.NUM_LAYERS])])
        # Output layer
        self.head = nn.Linear(config[VBS.DIM_EMBEDDING], len(config["vocab_decoder"]), bias=False)
        # Init
        self.apply(self._init_weights)
        self.optimizer = None
        self.Alpha_LabelSmoothing = None
        self.TokenWeight = None
        # logger.info("number of parameters: %e", sum(p.numel() for p in self.parameters()))

    def _set_train_params(self,Config):
        self.Alpha_LabelSmoothing = Config["Alpha_LabelSmoothing"]
        self.TokenWeight = Config["TokenWeight"]

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
        optimizer = torch.optim.Adam(self.parameters(), lr=train_config[VBS.RATE_LEARNING])
        return optimizer
    def init_scheduler(self,train_config):
        scheduler = torch.optim.lr_scheduler.StepLR(self.optimizer, step_size=train_config[VBS.SIZE_STEP], gamma=train_config[VBS.GAMMA])
        return scheduler
    def get_collate_fn(self, vocab_encoder,vocab_decoder):
        def collate(results):
            X_Encoder           = [a[0] for a in results]
            X_Decoder           = [a[1] for a in results]
            Auxiliary           = [a[2] for a in results]
            #
            max_len_x           = max([len(a) for a in X_Encoder])
            max_len_y           = max([len(a) for a in X_Decoder])
            #
            x                   = torch.tensor([(a+[vocab_encoder[VBS.TOKEN_PAD] for _ in range(max_len_x-len(a))]) for a in X_Encoder],dtype=torch.long)
            y                   = torch.tensor([(a+[vocab_decoder[VBS.TOKEN_PAD] for _ in range(max_len_y-len(a))]) for a in X_Decoder],dtype=torch.long)
            if isinstance(Auxiliary[0],list):
                MaxLen_Auxiliary    = max([len(TruthTable) for TruthTable in Auxiliary])
                Len_Vocab           = len(self.List_Vocab_Decoder)
                Auxiliary           = torch.tensor([TruthTable+[[0 for _ in range(Len_Vocab)] for _ in range(MaxLen_Auxiliary-len(TruthTable))] for TruthTable in Auxiliary])
            ##
            #
            return x,y,Auxiliary
        return collate
    def customize_model_fn(self,diex):
        def fn(diex):
            bos_token = diex[VBS.COLUMN_TASK_TYPE]
            # Encoder
            x_in = self.tokenizer(diex[VBS.COLUMN_ENCODER])
            if len(x_in)>0:
                x_in = [bos_token] + x_in + [VBS.TOKEN_END]
            x_in = [self.vocab_encoder[a] if a in self.vocab_encoder.keys() else self.vocab_encoder["<unk>"] for a in x_in ]
            # Decoder
            y_in = self.tokenizer(diex[VBS.COLUMN_DECODER])
            y_in = [bos_token] + y_in + [VBS.TOKEN_END]
            # Auxiliary
            ## 1. partial
            ## Is Valid
            TruthTable = []
            for CurrentIndex in range(1,len(y_in)):
                if (y_in[CurrentIndex] == "|" or "<" in y_in[CurrentIndex]) and y_in[CurrentIndex] != VBS.TOKEN_END:
                    TruthTable.append([0 for _ in range(len(self.List_Vocab_Decoder))])
                    continue
                CurrentTruthTable = []
                for CurrentToken in self.List_Vocab_Decoder:
                    try:
                        _ = ps.ParseSmiles("".join(y_in[1:CurrentIndex])+CurrentToken, partial=True)
                        IsValid = 1
                    except:
                        IsValid = 0
                    if CurrentToken == VBS.TOKEN_END:
                        CurrentSMI = join_scaf_deco(diex[VBS.COLUMN_ENCODER],"".join(y_in[1:CurrentIndex]))
                        if len(CurrentSMI) > 0:
                            IsValid = 1
                    CurrentTruthTable.append(IsValid)
                TruthTable.append(CurrentTruthTable)
                # StrPrint = "".join([f"{a:3}" for a in TruthTable])
                # print(f'''{y_in[i][:5]:5} {StrPrint}''')
            y_in = [self.vocab_decoder[a] if a in self.vocab_decoder.keys() else self.vocab_decoder["<unk>"] for a in y_in ]
            Auxiliary = TruthTable
            return x_in,y_in,Auxiliary
        return fn
    def generate_masks(self,X_Encoder, X_Decoder):
        with torch.no_grad():
            # Generate encoder, decoder, cross masks
            T = X_Decoder.shape[1]
            Mask_Encoder = (X_Encoder != self.Token_Padding_Encoder).unsqueeze(-2).unsqueeze(-2)
            Mask_Decoder = (X_Decoder != self.Token_Padding_Decoder).unsqueeze(-2).unsqueeze(-2).repeat(1,1,T,1)
            Mask_Cross   = (X_Encoder != self.Token_Padding_Encoder).unsqueeze(-2).unsqueeze(-2)
            mask_tril = torch.tril(torch.ones(T, T)).view(1, 1, T, T).to(Mask_Decoder.device)
            Mask_Decoder = Mask_Decoder.masked_fill(mask_tril==0,0)
        return Mask_Encoder,Mask_Decoder,Mask_Cross

    def forward(self, X_Encoder, X_Decoder, Y_Decoder_Ref=None,Auxiliary=None):
        Mask_Encoder, Mask_Decoder,Mask_Cross = self.generate_masks(X_Encoder, X_Decoder)
        # preprocess
        X_Encoder = self.Dropout1(self.Embedding_Encoder(X_Encoder) * math.sqrt(self.Dim_Embedding) + self.pos_emb(X_Encoder.size(1)))
        X_Decoder = self.Dropout2(self.Embedding_Decoder(X_Decoder) * math.sqrt(self.Dim_Embedding) + self.pos_emb(X_Decoder.size(1)))
        #### Now X_Encoder: BatchSize, SequenceLength, DimAttention         
        # Encoder blocks
        for encoder_block in self.encoder_blocks:
            X_Encoder = encoder_block(X_Encoder,Mask_Encoder)
        # X_Encoder = self.LayerNorm1(X_Encoder)
        # Decoder blocks
        for decoder_block in self.decoder_blocks:
            X_Decoder = decoder_block(X_Encoder,X_Decoder,Mask_Cross,Mask_Decoder)
        # X_Decoder = self.LayerNorm2(X_Decoder)
        Y_Decoder_Logits = self.head(X_Decoder)
        loss = None
        if Y_Decoder_Ref is not None:
            with torch.no_grad():
                Y_OneHot = F.one_hot(Y_Decoder_Ref, num_classes=len(self.vocab_decoder)) * (1-self.Alpha_LabelSmoothing)
                # LabelSmooth
                LabelSmooth = torch.ones(len(self.List_Vocab_Decoder),device = Y_Decoder_Ref.device) * self.Alpha_LabelSmoothing / (len(self.List_Vocab_Decoder)-1)
                Y_OneHot = Y_OneHot + LabelSmooth
                # PartialSMILES
                TruthTables = Auxiliary
                Y_OneHot = Y_OneHot * TruthTables
                # TokenWeight
                if self.TokenWeight is not None:
                    Weight = torch.tensor(
                        self.TokenWeight,
                        device = Y_Decoder_Ref.device).unsqueeze(0).unsqueeze(0)
                    Y_OneHot = Y_OneHot * Weight
                # IgnoreIndex
                Y_OneHot[Y_Decoder_Ref==self.Token_Padding_Decoder] = 0.
            Y_Decoder_Logits_LogSoftmax = F.log_softmax(Y_Decoder_Logits,dim=-1)
            loss = -(Y_OneHot * Y_Decoder_Logits_LogSoftmax).sum(dim=-1)
            loss = loss.mean()
            # loss2 = F.kl_div(F.log_softmax(Y_Decoder_Logits,dim=-1),F.one_hot(Y_Decoder_Ref,num_classes=Y_Decoder_Logits.shape[-1]).type_as(Y_Decoder_Logits))
        return Y_Decoder_Logits, loss



# self = trainer.model_module
# X_Encoder = trainer.X_Encoder
# X_Decoder = trainer.X_Decoder
# Y_Decoder_Ref = trainer.Y_Decoder_Ref
# Auxiliary = trainer.Auxiliary

# from torch.nn import functional as F
# Y_OneHot = F.one_hot(trainer.Y_Decoder_Ref,num_classes=len(trainer.model.vocab_decoder))
# import math
# import logging
# import torch
# import torch.nn as nn
# from torch.nn import functional as F
# # logger = logging.getLogger(__name__)
# from SCMG.config import varables as VBS
# from torch.autograd import Variable

# from SmilesPE.pretokenizer  import atomwise_tokenizer
# class debug1():
#     def __init__(self):
#         self.tokenizer = atomwise_tokenizer
#         self.vocab_encoder = torch.load("vocab_atom.pt")
#         self.vocab_decoder = torch.load("vocab_atom.pt")
    

# self = debug1()
# bos_token = "bos_token"
# diex={
#     VBS.COLUMN_ENCODER:"[*]c1cc(NC(=O)c2ccccc2)ccc1F",
#     VBS.COLUMN_DECODER:"[*]c1cc(NC(=O)c2cc3c(cn2)OCCO3)ccc1F",
#     VBS.COLUMN_TASK_TYPE:"<scmg_char_rand>",
#     VBS.TOKEN_END:"<pad>",
# }
# customize_model_fn(self,diex)


# rm -r checkpoints/TFdebug9_512_512_6_20220401_0
# python -i scripts/create_model_SCMG.py \
#   --model_type=Transformer_debug9 \
#   --model_name=TF_512_512_6_debug9 \
#   --num_decoder_layers=6 \
#   --num_heads=8 \
#   --dim_attention=512 \
#   --dim_feedforward=2048 \
#   --dim_embedding=512 \
#   --rate_dropout=0.2 \
#   --tokenizer=atom \
#   --size_block=300 \
#   --filepath_vocab_encoder=vocab_atom.pt \
#   --filepath_vocab_decoder=vocab_atom.pt \
#   --dirpath_checkpoint=checkpoints/TFdebug9_512_512_6_20220401_0

# python \
#   -i \
#   scripts/train/train_SCMG.py \
#   --dirpath_data=PreProcess_DecoderOnly/TrainingSets_EncoderDecoder_OneDecoder/ \
#   --size_batch=192 \
#   --size_step=1500 \
#   --rate_learning=0.0001 \
#   --gamma=0.1 \
#   --num_workers=32 \
#   --epochs=49 \
#   --dirpath_checkpoint=checkpoints/TFdebug9_512_512_6_20220401_0/ \
#   --log_level=INFO \
#   --run_one_epoch=0 \
#   --dry_run=0 \
#   --dump=1 \
#   --Alpha_LabelSmoothing=0.1