from junshan_kit import ParametersHub, DataSets


# -------------------------------------------------------------
def training_group(training_group):
    print(f"--------------------- training_group ------------------")
    for g in training_group:
        print(g)
    print(f"-------------------------------------------------------")


def training_info(args, data_name, optimizer_name, hyperparams, Paras, model_name):
    if Paras["use_color"]:
        print("\033[90m" + "-" * 115 + "\033[0m")
        print(
            f"\033[32m✅ \033[34mDataset:\033[32m {data_name}, \t\033[34mBatch-size:\033[32m {args.bs}, \t\033[34m(training, test) = \033[32m ({Paras['train_data_num']}, {Paras['test_data_num']}), \t\033[34m device:\033[32m {Paras['device']}"
        )
        print(
            f"\033[32m✅ \033[34mOptimizer:\033[32m {optimizer_name}, \t\033[34mParams:\033[32m {hyperparams}"
        )
        print(
            f'\033[32m✅ \033[34mmodel:\033[32m {model_name}, \t\033[34mmodel type:\033[32m {Paras["model_type"][model_name]},\t\033[34m loss_fn:\033[32m {Paras["loss_fn"]}'
        )
        print(f'\033[32m✅ \033[34mResults_folder:\033[32m {Paras["Results_folder"]}')
        print("\033[90m" + "-" * 115 + "\033[0m")

    else:
        print("-" * 115)
        print(
            f"✅ Dataset: {data_name}, \tBatch-size: {args.bs}, \t(training, test) = ({Paras['train_data_num']}, {Paras['test_data_num']}), \tdevice: {Paras['device']}"
        )
        print(f"✅ Optimizer: {optimizer_name}, \tParams: {hyperparams}")
        print(
            f"✅ model: {model_name}, \tmodel type: {Paras['model_type'][model_name]}, \tloss_fn: {Paras['loss_fn']}"
        )
        print(f"✅ Results_folder: {Paras['Results_folder']}")
        print("-" * 115)
        
# <Step_7_2>

def per_epoch_info(Paras, epoch, metrics, time):
    if Paras["use_color"]:
        print(
            f'\033[34m epoch = \033[32m{epoch+1}/{Paras["epochs"]}\033[0m,\t\b'
            f'\033[34m training_loss = \033[32m{metrics["training_loss"][epoch+1]:.4e}\033[0m,\t\b'
            f'\033[34m training_acc = \033[32m{100 * metrics["training_acc"][epoch+1]:.2f}\033[0m,\t\b'
            f'\033[34m time = \033[32m{time:.2f}\033[0m,\t\b')

    else:
        print(
            f"epoch = {epoch+1}/{Paras['epochs']},\t"
            f"training_loss = {metrics['training_loss'][epoch+1]:.4e},\t"
            f"training_acc = {100 * metrics['training_acc'][epoch+1]:.2f}%,\t"
            f"time = {time:.2f}"
        )

def print_per_epoch_info(epoch, Paras, epoch_loss, training_loss, training_acc, test_loss, test_acc, run_time):
    epochs = Paras["epochs"][Paras["data_name"]]
    # result = [(k, f"{v:.4f}") for k, v in run_time.items()]
    if Paras["use_color"]:
        print(
            f'\033[34m epoch = \033[32m{epoch+1}/{epochs}\033[0m,\t\b'
            f'\033[34m epoch_loss = \033[32m{epoch_loss[epoch+1]:.4e}\033[0m,\t\b'
            f'\033[34m train_loss = \033[32m{training_loss[epoch+1]:.4e}\033[0m,\t\b'
            f'\033[34m train_acc = \033[32m{100 * training_acc[epoch+1]:.2f}%\033[0m,\t\b'
            f'\033[34m test_acc = \033[32m{100 * test_acc[epoch+1]:.2f}%\033[0m,\t\b'
            f'\033[34m time (ep, tr, te) = \033[32m({run_time["epoch"]:.2f}, {run_time["train"]:.2f}, {run_time["test"]:.2f})\033[0m')
    else:
        print(
        f'epoch = {epoch+1}/{epochs},\t'
        f'epoch_loss = {epoch_loss[epoch+1]:.4e},\t'
        f'train_loss = {training_loss[epoch+1]:.4e},\t'
        f'train_acc = {100 * training_acc[epoch+1]:.2f}%,\t'
        f'test_acc = {100 * test_acc[epoch+1]:.2f}%,\t'
        f'time (ep, tr, te) = ({run_time["epoch"]:.2f}, {run_time["train"]:.2f}, {run_time["test"]:.2f})')


def all_data_info():
    print(ParametersHub.data_list.__doc__)

def data_info_DHI():
    data = DataSets.adult_income_prediction(print_info=True, export_csv=False)

def data_info_CCFD():
    data = DataSets.credit_card_fraud_detection(print_info=True, export_csv=False)

def data_info_AIP():
    data = DataSets.adult_income_prediction(print_info=True, export_csv=False)

def data_info_EVP():
    data = DataSets.electric_vehicle_population(print_info=True, export_csv=False)

def data_info_GHP():
    data = DataSets.global_house_purchase(print_info=True, export_csv=False)

def data_info_HL():
    data = DataSets.health_lifestyle(print_info=True, export_csv=False)

def data_info_HQC():
    data = DataSets.Homesite_Quote_Conversion(print_info=True)

def data_info_IEEE_CIS():
    data = DataSets.IEEE_CIS_Fraud_Detection(print_info=True)

def data_info_MICP():
    data = DataSets.medical_insurance_cost_prediction(print_info=True)

def data_info_PPE():
    data = DataSets.particle_physics_event_classification(print_info=True)
