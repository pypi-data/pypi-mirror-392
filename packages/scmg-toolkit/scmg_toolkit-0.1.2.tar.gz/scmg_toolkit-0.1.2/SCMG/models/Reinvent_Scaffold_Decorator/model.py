
Skip to content

    Why GitHub? 

Team
Enterprise
Explore
Marketplace
Pricing

Sign in
Sign up
undeadpixel /
reinvent-scaffold-decorator
Public

Code
Issues 3
Pull requests
Actions
Projects
Wiki
Security

    Insights

reinvent-scaffold-decorator/models/model.py /
Arús-Pous, Josep updated to revised version
Latest commit 37d0a8a on May 8, 2020
History
0 contributors
136 lines (118 sloc) 5.75 KB
"""
Model class.
"""

import torch
import torch.nn as tnn

import models.decorator as mdec


class DecoratorModel:

    def __init__(self, vocabulary, decorator, max_sequence_length=256, no_cuda=False, mode="train"):
        """
        Implements the likelihood and sampling functions of the decorator model.
        :param vocabulary: A DecoratorVocabulary instance with the vocabularies of both the encoder and decoder.
        :param network_params: A dict with parameters for the encoder and decoder networks.
        :param decorator: An decorator network instance.
        :param max_sequence_length: Maximium number of tokens allowed to sample.
        :param no_cuda: Forces the model not to use CUDA, even if it is available.
        :param mode: Mode in which the model should be initialized.
        :return:
        """
        self.vocabulary = vocabulary
        self.max_sequence_length = max_sequence_length
        self.network = decorator

        if torch.cuda.is_available() and not no_cuda:
            self.network.cuda()

        self._nll_loss = tnn.NLLLoss(reduction="none", ignore_index=0)
        self.set_mode(mode)

    @classmethod
    def load_from_file(cls, path, mode="train"):
        """
        Loads a model from a single file
        :param path: Path to the saved model.
        :param mode: Mode in which the model should be initialized.
        :return: An instance of the RNN.
        """
        data = torch.load(path)

        decorator = mdec.Decorator(**data["decorator"]["params"])
        decorator.load_state_dict(data["decorator"]["state"])

        model = DecoratorModel(
            decorator=decorator,
            mode=mode,
            **data["model"]
        )

        return model

    def save(self, path):
        """
        Saves the model to a file.
        :param path: Path to the file which the model will be saved to.
        """
        save_dict = {
            'model': {
                'vocabulary': self.vocabulary,
                'max_sequence_length': self.max_sequence_length
            },
            'decorator': {
                'params': self.network.get_params(),
                'state': self.network.state_dict()
            }
        }
        torch.save(save_dict, path)

    def set_mode(self, mode):
        """
        Changes the mode of the RNN to training or eval.
        :param mode: Mode to change to (training, eval)
        :return: The model instance.
        """
        if mode == "sampling" or mode == "eval":
            self.network.eval()
        else:
            self.network.train()
        return self

    def likelihood(self, scaffold_seqs, scaffold_seq_lengths, decoration_seqs, decoration_seq_lengths, with_attention_weights=False):
        """
        Retrieves the likelihood of a scaffold and its respective decorations.
        :param scaffold_seqs: (batch, seq) A batch of padded scaffold sequences.
        :param scaffold_seq_lengths: The length of the scaffold sequences (for packing purposes).
        :param decoration_seqs: (batch, seq) A batch of decorator sequences.
        :param decoration_seq_lengths: The length of the decorator sequences (for packing purposes).
        :return:  (batch) Log likelihood for each item in the batch.
        """

        # NOTE: the decoration_seq_lengths have a - 1 to prevent the end token to be forward-passed.
        logits, attention_weights = self.network(scaffold_seqs, scaffold_seq_lengths, decoration_seqs,
                                                 decoration_seq_lengths - 1)  # (batch, seq - 1, voc)
        log_probs = logits.log_softmax(dim=2).transpose(1, 2)  # (batch, voc, seq - 1)

        logits = self._nll_loss(log_probs, decoration_seqs[:, 1:]).sum(dim=1)  # (batch)
        if with_attention_weights:
            return logits, attention_weights
        else:
            return logits

    @torch.no_grad()
    def sample_decorations(self, scaffold_seqs, scaffold_seq_lengths):
        """
        Samples as many decorations as scaffolds in the tensor.
        :param scaffold_seqs: A tensor with the scaffolds to sample already encoded and padded.
        :param scaffold_seq_lengths: A tensor with the length of the scaffolds.
        :return: An iterator with (scaffold_smi, decoration_smi, nll) triplets.
        """
        batch_size = scaffold_seqs.size(0)
        input_vector = torch.full(
            (batch_size, 1), self.vocabulary.decoration_vocabulary["^"], dtype=torch.long).cuda()  # (batch, 1)
        seq_lengths = torch.ones(batch_size)  # (batch)
        encoder_padded_seqs, hidden_states = self.network.forward_encoder(scaffold_seqs, scaffold_seq_lengths)
        nlls = torch.zeros(batch_size).cuda()
        not_finished = torch.ones(batch_size, 1, dtype=torch.long).cuda()
        sequences = []
        for _ in range(self.max_sequence_length - 1):
            logits, hidden_states, _ = self.network.forward_decoder(
                input_vector, seq_lengths, encoder_padded_seqs, hidden_states)  # (batch, 1, voc)
            probs = logits.softmax(dim=2).squeeze()  # (batch, voc)
            log_probs = logits.log_softmax(dim=2).squeeze()  # (batch, voc)
            input_vector = torch.multinomial(probs, 1)*not_finished  # (batch, 1)
            sequences.append(input_vector)
            nlls += self._nll_loss(log_probs, input_vector.squeeze())
            not_finished = (input_vector > 1).type(torch.long)  # 0 is padding, 1 is end token
            if not_finished.sum() == 0:
                break

        decoration_smiles = [self.vocabulary.decode_decoration(seq)
                             for seq in torch.cat(sequences, 1).data.cpu().numpy()]
        scaffold_smiles = [self.vocabulary.decode_scaffold(seq) for seq in scaffold_seqs.data.cpu().numpy()]
        return zip(scaffold_smiles, decoration_smiles, nlls.data.cpu().numpy().tolist())








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
        T = X_Decoder.shape[1]
        Mask_Encoder = (X_Encoder != self.Token_Padding_Encoder).unsqueeze(-2).unsqueeze(-2)
        Mask_Decoder = (X_Decoder != self.Token_Padding_Decoder).unsqueeze(-2).unsqueeze(-2).repeat(1,1,T,1)
        Mask_Cross   = (X_Encoder != self.Token_Padding_Encoder).unsqueeze(-2).unsqueeze(-2)
        mask_tril = torch.tril(torch.ones(T, T)).view(1, 1, T, T).to(Mask_Decoder.device)
        Mask_Decoder = Mask_Decoder.masked_fill(mask_tril==0,0)
        return Mask_Encoder,Mask_Decoder,Mask_Cross

    def forward(self, X_Encoder, X_Decoder, Y_Decoder_Ref=None,boundary=None):
        Mask_Encoder, Mask_Decoder,Mask_Cross = self.generate_masks(X_Encoder, X_Decoder)
        # preprocess
        X_Encoder = self.Dropout1(self.Embedding_Encoder(X_Encoder) * math.sqrt(self.Dim_Attention) + self.pos_emb(X_Encoder.size(1)))
        X_Decoder = self.Dropout2(self.Embedding_Decoder(X_Decoder) * math.sqrt(self.Dim_Attention) + self.pos_emb(X_Decoder.size(1)))
        #### Now X_Encoder: BatchSize, SequenceLength, DimAttention         
        # Encoder blocks
        for encoder_block in self.encoder_blocks:
            X_Encoder = encoder_block(X_Encoder,Mask_Encoder)
        X_Encoder = self.LayerNorm1(X_Encoder)
        # Decoder blocks
        for decoder_block in self.decoder_blocks:
            X_Decoder = decoder_block(X_Encoder,X_Decoder,Mask_Cross,Mask_Decoder)
        X_Decoder = self.LayerNorm2(X_Decoder)
        Y_Decoder_Logits = self.head(X_Decoder)
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
