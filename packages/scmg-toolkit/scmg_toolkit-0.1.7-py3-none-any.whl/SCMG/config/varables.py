import re
from rdkit import Chem

DEFAULT = "default"
AUTO = "auto"

# Variables
COLUMN_SMILES = "SMILES"
COLUMN_ENCODER = "Encoder"
COLUMN_DECODER = "Decoder"
COLUMN_TASK_TYPE = "TaskType"
COLUMN_ENCODER_SEQUENCE = "EncoderSequence"
COLUMN_DECODER_SEQUENCE = "DecoderSequence"
COLUMN_BOS_TOKEN = "TokenBOS"
COLUMN_CUTS = "Cuts"
COLUMN_MIN_TOP_P = "MinTopP"
COLUMN_MIN_TOKEN_PROB = "MinTokenProb"
COLUMN_TOKEN_EOS_PROB = "TokenEOSProb"
COLUMN_MOLNAME = "MolName"
COLUMN_MOLINDEX = "MolIndex"
COLUMN_MOL_PROB = "MolProb"
COLUMN_MOL_PROB_TOPP = "MolProb_TopP"

# Task
TOKEN_BEGIN = "<bos>"
TOKEN_END = "<eos>"
TOKEN_SEP = "<sep>"
TOKEN_CODER_SEP = "<delim>"
# TRAIN = "Train"
TOKEN_PAD = "<pad>"
COLUMN_EXCLUDED_MIN = "ExcludedSize"
COLUMN_SIZE_ToRunForNExt = "ExcludedSize"
COLUMN_SIZE_EXCLUDED = "ExcludedSize"

# char_level_molecule_generation
COLUMN_task_char_mg = "char_mg"
TOKEN_TASK_CHAR_MG = "<char_mg>"

# char_level_scaffold_constrained_molecule_generation
COLUMN_task_char_scmg = "char_scmg"
TOKEN_TASK_SCMG_CHAR_RAND = "<scmg_char_rand>"
TOKEN_TASK_SCMG_CHAR_CANO = "<scmg_char_cano>"
TOKEN_TASK_DG_CHAR_RAND = "<dg_char_rand>"
TOKEN_TASK_DG_CHAR_CANO = "<dg_char_cano>"
LIST_HEAVY_ATOMS = ['c', 'C', 'O', 'N', 'n', 'F', '[C@H]', 'Cl', '[C@@H]', 'S', '[nH]', 's', 'o', 'Br', '[C@]', '[C@@]', 'P', 'B', '[N+]', '[P@@]', '[P@]', '[S@@]', '[N@+]', '[S@]', '[N@@+]', '[N-]', 'p']
COLUMN_EXCLUDE_REASON = "Excluded"
COLUMN_STATE = "State"
# chemical_property_prediction
COLUMN_task_chem_pd = "chem_pd"
TOKEN_TASK_CHEM_PD = "<chem_pd>"

# molecule_identification
COLUMN_task_mol_id = "mol_id"
TOKEN_TASK_MOL_ID = "<mol_id>"



FILEPATH_MODEL = "filepath_model"
FILEPATH_INPUT = "filepath_input"
DIRPATH_OUTPUT = "dirpath_output"
RANDOM_AUGUMENT = "random_augument"
TOP_P = "top_p"
TOP_K = "top_k"
MIN_MOL_PROB = "minimum_mol_prob"
MIN_TOKEN_PROB = "minimum_token_prob"
MAX_HEAVY_ATOMS = "maximum_heavy_atoms"
TEMPERATURE = "temperature"

# Data
VOCAB = "vocab"
SIZE_VOCAB = "size_vocab"
FILENAME_VOCAB = "vocab.pt"
FILENAME_VOCABSTATE = "vocabstate.pt"
FILENAME_DATA_RAW = "data.csv"

TRAIN = "train"
TEST = "test"
FILENAME_TRAIN_RAW = "train.pt"
FILENAME_TRAIN_EPOCH = lambda x: "train_"+str(x)+".pt"

FILENAME_TEST = "test.pt"
FILENAME_TEST_RAW = "test.pt"
FILENAME_TEST_EPOCH = lambda x: "test_"+str(x)+".pt"
FILEPATH_VOCAB = "filepath_vocab"
#
# try:
#     config.screen_width = os.get_terminal_size()[0]
# except:
#     config.screen_width = 141
MAX_SEQUENCE_LENGTH = "max_sequence_length"
COLUMN_INCHIKEY = "InchiKey"
# Train
MODEL_NAME = "model_name"
MODEL_TYPE = "model_type"
MODEL = "model"
TASKS = "tasks"
DIRPATH_CHECKPOINT = "dirpath_checkpoint"
DIRPATH_DATA = "dirpath_data"
SIZE_BATCH = "size_batch"
SIZE_BLOCK = "size_block"
RATE_LEARNING = "rate_learning"
DEVICE = "device"
EPOCH           = "epoch"
EPOCHS           = "epochs"
NUM_WORKERS = "num_workers"
DIRPATH_COMPLETED = "dirpath_completed"
DIRPATH_EXCLUDED = "dirpath_excluded"
DIRPATH_SBATCH = "dirpath_sbatch"

# Stats
TRAIN_LOSS      = "train_loss"
TEST_LOSS       = "test_loss"
TIME_ELAPSED    = "time_elapsed"
RATE_LEARNING   = "rate_learning"
TOKENS          = "tokens"

# Model
FILENAME_MODEL_INIT = "model_init.pt"
FILENAME_MODEL_LATEST = "model.pt"
FILENAME_MODEL_TRAINED = lambda x: "model_"+str(x)+".pt"

FILENAME_MODELSTATE_INIT = "modelstate_init.pt"
FILENAME_MODELSTATE_LATEST = "modelstate.pt"
FILENAME_MODELSTATE_TRAINED = lambda x: "modelstate_"+str(x)+".pt"

FILENAME_SCHEDULER_INIT = "scheduler_init.pt"
FILENAME_SCHEDULER_LATEST = "scheduler.pt"
FILENAME_SCHEDULER_TRAINED = lambda x: "scheduler_"+str(x)+".pt"

FILENAME_OPTIMIZER_INIT = "optimizer_init.pt"
FILENAME_OPTIMIZER_LATEST = "optimizer.pt"
FILENAME_OPTIMIZER_TRAINED = lambda x: "optimizer_"+str(x)+".pt"

# FILENAME_TRAINLOG_INIT = "train_init.pt"
FILENAME_TRAINSTATS_LATEST = "trainstats_latest.csv"
FILENAME_TRAINSTATS_TRAINED = lambda x: "trainstats_"+str(x)+".csv"

FILENAME_TRAINLOG = "train"
FORMAT_TIMESTAMP_FILEHANDLER = "%Y%m%d%H%M%S_%f.log"
FORMAT_TIMESTAMP = "%Y/%m/%d %H:%M:%S %f"

FORMAT_LOG = ""
DRY_RUN = "dry_run"
LOG_LEVEL = "log_level"
TOKENIZER = "tokenizer"
RUN_ONE_EPOCH = "run_one_epoch"
# # Column names
# IS_NOVEL = "IS_NOVAL"
# NOVALTY = "Novalty"
# # VALIDITY = "Validity"
# IS_VALID = "IS_VALID"
# IS_NOVAL = "IS_NOVAL"
# DIR_SAVE = "dir_save"
# MODEL_LATEST = "model.pt"
# LOG_TRAIN_LATEST = "train_log.csv"
# OPTIMIZER_LATEST = "optimizer.pt"
# SCHEDULER_LATEST = "scheduler.pt"
# TRAIN_LOSS      = "train_loss"
# TEST_LOSS       = "test_loss"
# TIME_ELAPSED    = "time_elapsed"
# # LR              = "lr"
# TOKENS          = "tokens"

LOGP = "logP"
WEIGHT = "weight"
QED = "QED"
VALIDITY = "SMILES_VALID"
FILENAME_TRAIN_DIST = "train_dist.pt"
FILENAME_TEST_DIST = "test_dist.pt"
MODEL_PRETRAIN = "model_pretrained.pt"

PYFILE_SAMPLER = "sampler.py"
PYFILE_TRAINER = "trainer.py"
PYFILE_DATALOADER = "dataloader.py"
# PYFILE_SAMPLER = "sampler.py"




# Model parameters
NUM_LAYERS = "num_layers"
NUM_ENCODER_LAYERS = "num_encoder_layers"
NUM_DECODER_LAYERS = "num_decoder_layers"
NUM_HEADS = "num_heads"
DIM_ATTENTION = "dim_attention"
DIM_FEEDFORWARD = "dim_feedforward"
DIM_LSTM = "dim_lstm"
DIM_EMBEDDING = "dim_embedding"
DIM_OUTPUT = "dim_output"
RATE_DROPOUT = "rate_dropout"




#Scheduler
SIZE_STEP = "size_step"
GAMMA = "gamma"








# From Reinvent-Scaffold-Decorator
ATTACHMENT_POINT_TOKEN = "*"
ATTACHMENT_POINT_NUM_REGEXP = r"\[{}:(\d+)\]".format(re.escape(ATTACHMENT_POINT_TOKEN))
ATTACHMENT_POINT_REGEXP = r"(?:{0}|\[{0}[^\]]*\])".format(re.escape(ATTACHMENT_POINT_TOKEN))
ATTACHMENT_POINT_NO_BRACKETS_REGEXP = r"(?<!\[){}".format(re.escape(ATTACHMENT_POINT_TOKEN))

ATTACHMENT_SEPARATOR_TOKEN = "|"

SLICE_SMARTS = {
    "hr": [
        "[*]!@-[*]"
    ],
    "recap": [
        "[C;$(C=O)]!@-N",  # amides and urea
        "[C;$(C=O)]!@-O",  # esters
        "C!@-[N;!$(NC=O)]",  # amines
        "C!@-[O;!$(NC=O)]",  # ether
        "[CX3]!@=[CX3]",  # olefin
        "[N+X4]!@-C",  # quaternary nitrogen
        "n!@-C",  # aromatic N - aliphatic C
        "[$([NR][CR]=O)]!@-C",  # lactam nitrogen - aliphatic carbon
        "c!@-c",  # aromatic C - aromatic C
        "N!@-[$(S(=O)=O)]"  # sulphonamides
    ]
}
SLICE_SMARTS = {name: [Chem.MolFromSmarts(sma) for sma in smarts] for name, smarts in SLICE_SMARTS.items()}



