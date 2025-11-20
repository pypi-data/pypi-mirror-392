import numpy as np
import sys, os, torch, random, glob
import argparse
from datetime import datetime
import junshan_kit.ModelsHub as ModelsHub


class check_args: 
    def __init__(self):
        pass

    def get_args(self):
        parser = argparse.ArgumentParser(description="Combined config argument example")

        allowed_models = ["LS", "LRBL2", "ResNet18"]

        allowed_optimizers = ["ADAM",
                            "SGD", 
                            "Bundle",
                            "ALR_SMAG",
                            "SPBM_TR",
                            "SPBM_PF",
                            "SPSmax",
                            "SPBM_TR_NoneSpecial",
                            "SPBM_TR_NoneLower",
                            "SPBM_PF_NoneLower",
                            ]

        allowed_datasets = ["MNIST", 
                            "CIFAR100",
                            "AIP", 
                            "CCFD",
                            "Duke",
                            "Ijcnn",
                            "DHI",
                            "EVP",
                            ]

        optimizers_mapping = {
            "ADAM": "ADAM",
            "SGD": "SGD",
            "Bundle": "Bundle",
            "ALR_SMAG": "ALR-SMAG",
            "SPBM_TR": "SPBM-TR",
            "SPBM_PF": "SPBM-PF",
            "SPSmax": "SPSmax",
            "SPBM_TR_NoneSpecial": "SPBM-TR-NoneSpecial",
            "SPBM_TR_NoneLower": "SPBM-TR-NoneLower",
            "SPBM_TR_NoneCut": "SPBM-TR-NoneCut",
            "SPBM_PF_NoneSpecial": "SPBM-PF-NoneSpecial",
            "SPBM_PF_NoneLower": "SPBM-PF-NoneLower",
            "SPBM_PF_NoneCut": "SPBM-PF-NoneCut"
        }

        model_mapping = {
            "LS": "LeastSquares",
            "LRBL2": "LogRegressionBinaryL2",
            "ResNet18": "ResNet18"
        }

        data_name_mapping = {
            "MNIST": "MNIST",
            "CIFAR100": "CIFAR100",
            "Duke": "Duke",
            "AIP": "Adult_Income_Prediction",
            "CCFD": "Credit_Card_Fraud_Detection",
            "Ijcnn": "Ijcnn",
            "DHI":"Diabetes_Health_Indicators",
            "EVP": "Electric_Vehicle_Population",
        }

        # Single combined argument that can appear multiple times
        parser.add_argument(
            "--train",
            type=str,
            nargs="+",                   # Allow multiple configs
            required=True,
            help = f"Format: model-dataset-optimizer (e.g., ResNet18-CIFAR100-ADAM). model: {model_mapping}, \n datasets: {allowed_datasets}, optimizers: {allowed_optimizers},"
        )

        parser.add_argument(
        "--e",
        type=int,
        required=True,
        help="Number of training epochs. Example: --e 50"
        )

        parser.add_argument(
            "--seed",
            type=int,
            default=42,
            help="Random seed for experiment reproducibility. Default: 42"
        )

        parser.add_argument(
            "--bs",
            type=int,
            required=True,
            help="Batch size for training. Example: --bs 128"
        )

        parser.add_argument(
            "--cuda",
            type=int,
            default=0,
            required=True,
            help="The number of cuda. Example: --cuda 1 (default=0) "
        )

        parser.add_argument(
            "--s",
            type=float, 
            default=1.0, 
            # required=True,
            help="Proportion of dataset to use for training split. Example: --s 0.8 (default=1.0)"
        )

        parser.add_argument(
        "--subset",
        type=float,
        nargs=2,
        # required=True,
        help = "Two subset ratios (train, test), e.g., --subset 0.7 0.3 or --subset 500 500"
        )

        parser.add_argument(
        "--time_str",
        type=str,
        nargs=1,
        # required=True,
        help = "the str of time"
        )

        parser.add_argument(
        "--send_email",
        type=str,
        nargs=3,
        # required=True,
        help = "from_email to_email, from_pwd"
        )

        parser.add_argument(
        "--user_search_grid",
        type=int,
        nargs=1,
        # required=True,
        help = "search_grid: 1:True, 0:False"
        )

        args = parser.parse_args()
        args.model_name_mapping = model_mapping
        args.data_name_mapping = data_name_mapping
        args.optimizers_name_mapping = optimizers_mapping

        if args.subset is not None:
            self.check_subset_info(args, parser)

        self.check_args(args, parser, allowed_models, allowed_optimizers, allowed_datasets)

        return args

    def check_subset_info(self, args, parser):
        total = sum(args.subset)
        if args.subset[0]>1:
            # CHECK
            for i in args.subset:
                if i < 1:
                    parser.error(f"Invalid --subset {args.subset}: The number of subdata must > 1")    
        else:
            if abs(total - 1.0) != 0.0:  
                parser.error(f"Invalid --subset {args.subset}: the values must sum to 1.0 (current sum = {total:.6f}))")

    def check_args(self, args, parser, allowed_models, allowed_optimizers, allowed_datasets):
        # Parse and validate each train_group
        for cfg in args.train:
            try:
                model, dataset, optimizer = cfg.split("-")

                if model not in allowed_models:
                    parser.error(f"Invalid model '{model}'. Choose from {allowed_models}")
                if optimizer not in allowed_optimizers:
                    parser.error(f"Invalid optimizer '{optimizer}'. Choose from {allowed_optimizers}")
                if dataset not in allowed_datasets:
                    parser.error(f"Invalid dataset '{dataset}'. Choose from {allowed_datasets}")

            except ValueError:
                parser.error(f"Invalid format '{cfg}'. Use model-dataset-optimizer")

        for cfg in args.train:
            model_name, dataset_name, optimizer_name = cfg.split("-")
            try:
                f = getattr(ModelsHub, f"Build_{args.model_name_mapping[model_name]}_{args.data_name_mapping[dataset_name]}")

            except:
                print(getattr(ModelsHub, f"Build_{args.model_name_mapping[model_name]}_{args.data_name_mapping[dataset_name]}"))
                assert False

def UpdateOtherParas(args, OtherParas):
    if args.time_str is not None:
        time_str = args.time_str[0]
    else:
        time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    if args.send_email is not None:
        debug = False
    else:
        debug = True
    
    if args.user_search_grid[0] == 1:
        OtherParas["user_search_grid"] = True
    else:
        OtherParas["user_search_grid"] = False
    
    OtherParas["time_str"] = time_str
    OtherParas["debug"] = debug

    return OtherParas

def get_train_group(args):
    training_group = []
    for cfg in args.train:
        model, dataset, optimizer = cfg.split("-")
        training_group.append((args.model_name_mapping[model], args.data_name_mapping[dataset], args.optimizers_name_mapping[optimizer]))

    return training_group


def set_paras(args, OtherParas):
    Paras = {
        # Name of the folder where results will be saved.
        "results_folder_name": OtherParas["results_folder_name"],

        # Print loss every N epochs.
        "epoch_log_interval": 1,

        "use_log_scale": True,
        
        # Timestamp string for result saving.
        "time_str": OtherParas["time_str"],

        # Random seed
        "seed": args.seed,

        # Device used for training.
        "cuda": f"cuda:{args.cuda}",

        # batch-size 
        "batch_size": args.bs,

        # epochs
        "epochs": args.e,

        # split_train_data
        "split_train_data": args.s,

        # select_subset
        "select_subset": args.subset,

        # Results_dict
        "Results_dict": {},

        # type: bool
        "user_search_grid": OtherParas["user_search_grid"],
    }

    Paras = model_list(Paras)
    Paras = model_type(Paras)
    Paras = data_list(Paras)
    Paras = optimizer_paras_dict(Paras, OtherParas)
    Paras = device(Paras)
        
    return Paras


def set_seed(seed=42):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def device(Paras) -> dict:
    device = torch.device(f"{Paras['cuda']}" if torch.cuda.is_available() else "cpu")
    Paras["device"] = device
    use_color = sys.stdout.isatty()
    Paras["use_color"] = use_color

    return Paras

def model_list(Paras) -> dict:
    model_list = [
        "ResNet18",
        "ResNet34",
        "LeastSquares",
        "LogRegressionBinary",
        "LogRegressionBinaryL2",
    ]
    Paras["model_list"] = model_list
    return Paras

def model_type(Paras) -> dict:
    model_type = {
        "ResNet18": "multi",
        "ResNet34": "multi",
        "LeastSquares": "multi",
        "LogRegressionBinary": "binary",
        "LogRegressionBinaryL2": "binary",
    }

    Paras["model_type"] = model_type
    return Paras

def data_list(Paras) -> dict:
    """
    Attach a predefined list of dataset names to the parameter dictionary.

    The predefined datasets include:
    - Duke:
        - classes: 2
        - data: 42 (38 + 4)
        - features: 7,129
    - Ijcnn:
        - classes: 2
        - data: (35,000 + 91,701)
        - features: 22
    - w8a:
        - classes: 2
        - data: (49,749 + 14,951)
        - features: 300
    - RCV1
    - Shuttle
    - Letter
    - Vowel
    - MNIST
    - CIFAR100
    - CALTECH101_Resize_32
    - Adult Income Prediction
        - 
    - Credit_Card_Fraud_Detection
    """

    data_list = [
        "Duke",
        "Ijcnn",
        "w8a",
        "RCV1",
        "Shuttle",
        "Letter",
        "Vowel",
        "MNIST",
        "CIFAR100",
        "CALTECH101_Resize_32",
        "Adult_Income_Prediction",
        "Credit_Card_Fraud_Detection",
        "Diabetes_Health_Indicators",
        "Electric_Vehicle_Population",
    ]
    Paras["data_list"] = data_list
    return Paras


def optimizer_paras_dict(Paras, OtherParas)->dict:
    optimizer_dict = {
    # ----------------- ADAM --------------------
    "ADAM": {
        "params": {
            # "alpha": [2 * 1e-3],
            "alpha": (
                [0.5 * 1e-3, 1e-3, 2 * 1e-3]
                if OtherParas["SeleParasOn"]
                else [1e-3]
            ),
            "epsilon": [1e-8],
            "beta1": [0.9],
            "beta2": [0.999],
        },
    },
    # ------------- ALR-SMAG --------------------
    "ALR-SMAG": {
        "params": {
            "c": ([0.1, 0.5, 1, 5, 10] if OtherParas["SeleParasOn"] else [0.1]),
            "eta_max": (
                [2**i for i in range(-8, 9)]
                if OtherParas["SeleParasOn"]
                else [0.125]
            ),
            "beta": [0.9],
        },
    },
    # ------------ Bundle -----------------------
    "Bundle": {
        "params": {
            "delta": (
                [2**i for i in range(-8, 9)]
                if OtherParas["SeleParasOn"]
                else [0.01]
            ),
            "cutting_number": [10],
        },
    },
    # ------------------- SGD -------------------
    "SGD": {
        "params": {
            "alpha": (
                [2**i for i in range(-8, 9)] if OtherParas["SeleParasOn"] else [0.001]
            )
        }
    },
    # ------------------- SPSmax ----------------
    "SPSmax": {
        "params": {
            "c": ([0.1, 0.5, 1, 5, 10] if OtherParas["SeleParasOn"] else [0.1]),
            "gamma": (
                [2**i for i in range(-8, 9)]
                if OtherParas["SeleParasOn"]
                else [0.125]),
        },
    },
    # -------------- SPBM-PF --------------------
    "SPBM-PF": {
        "params": {
            "M": [1e-5],
            "delta": (
                [2**i for i in range(9, 20)]
                if OtherParas["SeleParasOn"]
                else [1]
            ),
            "cutting_number": [10],
        },
    },
    # -------------- SPBM-TR --------------------
    "SPBM-TR": {
        "params": {
            "M": [1e-5],
            "delta": (
                [2**i for i in range(9, 20)]
                if OtherParas["SeleParasOn"]
                else [256]
            ),
            "cutting_number": [10],
        },
    },
    
    # ----------- SPBM-TR-NoneLower -------------
    "SPBM-TR-NoneLower": {
        "params": {
            "M": [1e-5],
            "delta": (
                [2**i for i in range(0, 9)]
                if OtherParas["SeleParasOn"]
                else [256]
            ),
            "cutting_number": [10],
        },
    },
    # ----------- SPBM-TR-NoneSpecial -----------
    "SPBM-TR-NoneSpecial": {
        "params": {
            "M": [1e-5],
            "delta": (
                [2**i for i in range(-8, 9)]
                if OtherParas["SeleParasOn"]
                else [1]
            ),
            "cutting_number": [10],
        },
    },
    # ------------- SPBM-PF-NoneLower -----------
    "SPBM-PF-NoneLower": {
        "params": {
            "M": [1e-5],
            "delta": (
                [2**i for i in range(0, 9)]
                if OtherParas["SeleParasOn"]
                else [0]
            ),

            "cutting_number": [10],
        },
    },
    }

    Paras["optimizer_search_grid"] = optimizer_dict
    return Paras

def metrics()->dict:
    metrics = {
        "epoch_loss": [],
        "training_loss": [],
        "test_loss": [],
        "iter_loss": [],
        "training_acc": [],
        "test_acc": [],
        "grad_norm": [],
        "per_epoch_loss": []
    }
    return metrics


def hyperparas_and_path(Paras, model_name, data_name, optimizer_name, params_gird):

    keys, values = list(params_gird.keys()), list(params_gird.values())

    Paras["Results_folder"] = f'./{Paras["results_folder_name"]}/seed_{Paras["seed"]}/{model_name}/{data_name}/{optimizer_name}/train_{Paras["train_data_num"]}_test_{Paras["test_data_num"]}/Batch_size_{Paras["batch_size"]}/epoch_{Paras["epochs"]}/{Paras["time_str"]}'
    os.makedirs(Paras["Results_folder"], exist_ok=True)

    return keys, values, Paras


def fig_ylabel(str_name):

    ylabel = {
        "training_loss": "training loss",
        "test_loss": "test loss",
        "training_acc": "training accuracy",
        "test_acc": "test accuracy",
        "grad_norm": "grad norm",
        "per_epoch_loss": "per epoch loss",
        "epoch_loss": "epoch loss",
    }
    return ylabel[str_name]


def model_abbr(model_name):

    name_map = {
        "LogRegressionBinaryL2": "LRBL2",
        "ResNet18": "ResNet18",
        "ResNet34": "ResNet34",
        "LstSquares": "LS"
    }
    return name_map[model_name]


def dataset_abbr(model_name):

    name_map = {
        "MNIST": "MNIST",
        "CIFAR100": "CIFAR100",
        "Duke": "Duke",
        "Ijcnn": "Ijcnn",
        "Adult_Income_Prediction": "AIP",
        "Credit_Card_Frau_Detection": "CCFD",
        "Diabetes_Health_Indicators": "DHI",
        "Electric_Vehicle_Population": "EVP",
        "Global_House_Purchase": "GHP",
        "Health_Lifestyle": "HL",
    }
    return name_map[model_name]

def dataset_full_name(model_name):

    name_map = {
        "MNIST": "MNIST",
        "CIFAR100": "CIFAR100",
        "Duke": "Duke",
        "AIP": "Adult_Income_Prediction",
        "CCFD": "Credit_Card_Fraud_Detection",
        "Ijcnn": "Ijcnn",
        "DHI":"Diabetes_Health_Indicators",
        "EVP": "Electric_Vehicle_Population",
    }
    return name_map[model_name]

def user_paras_grid(Paras):
    pass



def opt_paras_str(opt_paras_dict):
    """
    Convert optional parameters dictionary to a formatted string representation.

    This function iterates through key-value pairs in the input dictionary,
    concatenating all key-value pairs except "ID" into an underscore-separated
    string with the format "key_value".

    Args:
        opt_paras_dict (dict): A dictionary containing optional parameters,
                            where keys are parameter names and values are parameter values

    Returns:
        str: Formatted parameter string in the format "k1_v1_k2_v2_...",
        excluding the ID parameter
    """

    keys = list(opt_paras_dict.keys())
    values = list(opt_paras_dict.values())

    param_str = "_".join(f"{k}_{v}" for k, v in zip(keys, values) if k != "ID")

    return param_str
# <set_marker_point>
def set_marker_point(epoch_num: int) -> list:
    marker_point = {
        1: [0],
        4: [0, 2, 4],
        6: [0, 2, 4, 6],
        8: [0, 2, 4, 6, 8],
        10: [0, 2, 4, 6, 8, 10],
        100: [0, 20, 40, 60, 80, 100],
        200: [0, 40, 80, 120, 160, 200],
    }
    if epoch_num not in marker_point:
        raise ValueError(f"No marker defined for epoch {epoch_num}")
    
    return marker_point[epoch_num]

# <set_marker_point>
# <results_path_to_info>
def results_path_to_info(path_list):
    info_dict = {}

    for path in path_list:
        parts = path.split("/")
        seed = parts[1]
        model_name = parts[2]
        data_name = parts[3]
        optimizer = parts[4]
        train_test = parts[5].split("_")
        batch_size = parts[6].split("_")[2]
        epochs = parts[7].split("_")[1]
        ID = parts[8]

        if model_name not in info_dict:
            info_dict[model_name] = {}
        
        if data_name not in info_dict[model_name]:
            info_dict[model_name][data_name] = {}
        
        if optimizer not in info_dict[model_name][data_name]:
            info_dict[model_name][data_name][optimizer] = {}

        info_dict[model_name][data_name][optimizer][ID] = {
            "seed": seed.split("_")[1],
            "epochs": int(epochs),
            "train_test": (train_test[1], train_test[3]),
            "batch_size": batch_size,
            "marker": set_marker_point(int(epochs)),
            "optimizer":{
                f"{optimizer}":{
                    "ID": ID,
                    }
                }
        }

    return info_dict
# <results_path_to_info>

# <update_info_dict>
def update_info_dict(draw_data_list, draw_data, results_dict, model_name, info_dict, metric_key_dict):
    for data_name in draw_data_list:
        for i in draw_data[data_name]:
            optimizer_name, ID, Opt_Paras = i

            if data_name not in results_dict[model_name].keys():
                print('*' * 40)
                print(f'{data_name} not in results')
                print('*' * 40)
                assert False

            # Check if optimizer_name exists in results_dict
            if optimizer_name not in results_dict[model_name][data_name]:
                print('*' * 40)
                print(f'({data_name}, {optimizer_name}, {ID}) not in results_dict and \n {optimizer_name} is error.')
                print('*' * 40)
                assert False

            # Check if ID exists in results_dict
            if ID not in results_dict[model_name][data_name][optimizer_name]:
                print('*' * 60)
                print(f'({data_name}, {optimizer_name}, {ID}) not in results_dict and \n {ID} is error.')
                print('*' * 60)
                assert False

            # Initialize info_dict[data_name] if it does not exist
            if data_name not in info_dict:
                info_dict[data_name] = results_dict[model_name][data_name][optimizer_name][ID].copy()

            # Update optimizer parameters
            if "optimizer" not in info_dict[data_name]:
                info_dict[data_name]["optimizer"] = {}
            info_dict[data_name]["optimizer"][optimizer_name] = Opt_Paras
            info_dict[data_name]["optimizer"][optimizer_name]["ID"] = ID

            # Update metric_key
            info_dict[data_name]["metric_key"] = metric_key_dict[data_name]
    
    return info_dict
# <update_info_dict>

def get_results_all_pkl_path(results_folder):

    pattern = os.path.join(results_folder, "**", "*.pkl")

    return glob.glob(pattern, recursive=True)