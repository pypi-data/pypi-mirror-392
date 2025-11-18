import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.nn.utils.rnn as rnn_utils
from SCMG.config import varables

class Model(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.vocab = config["vocab_encoder"]
        # self.vocabulary = vocabulary
        # self.hidden_size = config.hidden
        # self.num_layers = config.num_layers
        # self.dropout = config.dropout
        # self.vocab_size = self.input_size = self.output_size = len(vocabulary)
        self.embedding_layer = nn.Embedding(len(config["vocab_encoder"]), config[varables.DIM_EMBEDDING])
        self.lstm_layer = nn.LSTM(config[varables.DIM_EMBEDDING], config[varables.DIM_LSTM],
                                  config[varables.NUM_LAYERS], dropout=config[varables.RATE_DROPOUT],
                                  batch_first=True)
        self.linear_layer = nn.Linear(config[varables.DIM_LSTM], len(config["vocab_encoder"]))
    def get_collate_fn(self, vocab_encoder,vocab_decoder):
        def collate(results):
            x_in = None
            y_in = [a[0] + [vocab_encoder[varables.TOKEN_SEP]] + a[1] for a in results]
            # boundary = [a[2] for a in results]
            max_len = max([len(a) for a in y_in])
            y = torch.tensor([(a+[vocab_encoder[varables.TOKEN_PAD]]*(max_len-len(a))) for a in y_in],dtype=torch.long)
            return x_in,y,0
        return collate
    def init_optimizers(self,train_config):
        optimizer = torch.optim.Adam(self.parameters(), lr=train_config[varables.RATE_LEARNING])
        return optimizer
    def init_scheduler(self,train_config):
        scheduler = torch.optim.lr_scheduler.StepLR(self.optimizer, step_size=train_config[varables.SIZE_STEP], gamma=train_config[varables.GAMMA])
        return scheduler
    def forward(self, src, trg, trg_out, boundary=None):
        # x = ([src , torch.tensor([self.vocab["<sep>"]]*x.size[0]).unsqueeze(1).to(x.device), trg],dim=1)
        hiddens=None
        x = self.embedding_layer(trg)
        # x = rnn_utils.pack_padded_sequence(x, lengths, batch_first=True)
        self.lstm_layer.flatten_parameters()
        x, hiddens = self.lstm_layer(x, hiddens)
        # x, _ = rnn_utils.pad_packed_sequence(x, batch_first=True)
        logits = self.linear_layer(x)
        loss = None
        if trg_out is not None:
            loss = F.cross_entropy(logits.view(-1, logits.size(-1)), trg_out.view(-1))
        return logits, loss
