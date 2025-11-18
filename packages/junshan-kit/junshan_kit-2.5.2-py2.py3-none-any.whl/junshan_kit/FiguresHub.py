"""
----------------------------------------------------------------------
>>> Author       : Junshan Yin
>>> Last Updated : 2025-11-14
----------------------------------------------------------------------
"""
import math
import matplotlib.pyplot as plt
from junshan_kit import ParametersHub

def marker_schedule(marker_schedule=None):
    if marker_schedule == "SPBM":
        based_marker = {
            "ADAM": "s",  # square
            "ALR-SMAG": "h",  # pixel marker
            "Bundle": "o",  # circle
            "SGD": "p",  # pentagon
            "SPSmax": "4",  # tri-right
            "SPBM-PF": "*",  # star
            "SPBM-TR": "s",  # star
        }
    else:

        based_marker = {
            "point": ".",  # point marker
            "pixel": ",",  # pixel marker
            "circle": "o",  # circle
            "triangle_down": "v",  # down triangle
            "triangle_up": "^",  # up triangle
            "triangle_left": "<",  # left triangle
            "triangle_right": ">",  # right triangle
            "tri_down": "1",  # tri-down
            "tri_up": "2",  # tri-up
            "tri_left": "3",  # tri-left
            "tri_right": "4",  # tri-right
            "square": "s",  # square
            "pentagon": "p",  # pentagon
            "star": "*",  # star
            "hexagon1": "h",  # hexagon 1
            "hexagon2": "H",  # hexagon 2
            "plus": "+",  # plus
            "x": "x",  # x
            "diamond": "D",  # diamond
            "thin_diamond": "d",  # thin diamond
            "vline": "|",  # vertical line
            "hline": "_",  # horizontal line
        }

    return based_marker


def colors_schedule(colors_schedule=None):

    if colors_schedule == "SPBM":
        based_color = {
            "ADAM":      "#7f7f7f",  # gray
            "ALR-SMAG":  "#8fbc8f",  # olive
            "Bundle":    "#17becf",  # cyan
            "SGD":       "#2ca02c",  # green
            "SPSmax":    "#BA6262",  # brown
            "SPBM-PF":   "#1f77b4",  # blue
            "SPBM-TR":   "#d62728",  # red
        }
    else:
        based_color = {
            "ADAM":     "#1f77b4",
            "ALR-SMAG": "#ff7f0e",
            "Bundle":   "#2ca02c",
            "SGD":      "#d62728",
            "SPSmax":   "#9467bd",
            "SPBM-PF":  "#8c564b",
            "SPBM-TR":  "#e377c2",
            "dddd":     "#7f7f7f",
            "xxx":      "#bcbd22",
            "ED":       "#17becf",
        }
    return based_color


def Search_Paras(Paras, args, model_name, data_name, optimizer_name, metric_key = "training_loss"):

    param_dict = Paras["Results_dict"][model_name][data_name][optimizer_name]

    num_polts = len(param_dict)
    cols = 3
    rows = math.ceil(num_polts / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    axes = axes.flatten()

    for idx, (param_str, info) in enumerate(param_dict.items()):
        ax = axes[idx]
        metric_list = info.get(metric_key, [])
        # duration = info.get('duration', 0)
        ax.plot(metric_list)
        # ax.set_title(f"time:{duration:.8f}s - seed: {Paras['seed']}, ID: {Paras['time_str']} \n params = {param_str}", fontsize=10)
        ax.set_title(f"seed: {Paras['seed']}, ID: {Paras['time_str']} \n params = {param_str}", fontsize=10)
        ax.set_xlabel("epochs")
        ax.set_ylabel(ParametersHub.train_fig_ylabel(metric_key))
        ax.grid(True)
        if Paras.get('use_log_scale', "OFF") == "ON" and 'loss' or 'grad' in metric_key:
            ax.set_yscale("log")

    # Delete the redundant subfigures
    for i in range(len(param_dict), len(axes)):
        fig.delaxes(axes[i])

    

    plt.suptitle(f'{model_name} on {data_name} - {optimizer_name} (training/test samples: {Paras["train_data_num"]}/{Paras["test_data_num"]}), {Paras["device"]}', fontsize=16)
    plt.tight_layout(rect=(0, 0, 1, 0.9))

    filename = f"{Paras["Results_folder"]}/{metric_key}_{ParametersHub.model_abbr(model_name)}_{data_name}_{optimizer_name}.pdf"
    fig.savefig(filename)
    print(f"✅ Saved: {filename}")
    plt.close('all')


    

