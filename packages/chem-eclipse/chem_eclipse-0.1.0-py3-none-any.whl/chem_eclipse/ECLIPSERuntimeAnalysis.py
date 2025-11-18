import copy
import time
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib as mpl
from tqdm import trange
import json
import os
from chem_eclipse.models.ECLIPSEModel import ECLIPSEModel
from chem_eclipse.utils import get_arguments


def load_best_eclipse(dataframe, seed, args):
    eclipse = dataframe[dataframe["seed"] == seed]
    eclipse = eclipse.loc[(eclipse["val_f1"].idxmax())]
    base_path = eclipse.path.replace("\\", "/")
    with open(os.path.join(base_path, "config.json")) as c_file:
        config = json.load(c_file)
    with open(os.path.join(base_path, "split.json")) as s_file:
        split = json.load(s_file)
    ec_to_i = split["ec_to_i"]
    eclipse = ECLIPSEModel(ec_to_i, config, args, save_path=f"results/runtime/", device="cuda",
                     tolerance=eclipse.tolerance)
    eclipse = eclipse.load_model(path=base_path)
    return eclipse, split


def runtime_analysis(args):
    runtime_path = "results/summary/runtimes.json"
    if not os.path.exists(runtime_path):
        batch_sizes = [1, 10, 100, 1000]
        time_inner = {b: [] for b in batch_sizes}
        times = {"H eclipse": copy.deepcopy(time_inner), "F eclipse": copy.deepcopy(time_inner)}
        seeds = range(10)
        h_results = pd.read_csv("results/summary/hierarchy.csv")
        h_results = h_results[h_results["data_name"] == "ecmap"]
        f_results = pd.read_csv("results/summary/flat.csv")
        f_results = f_results[f_results["data_name"] == "ecmap"]
        for seed in seeds:
            h_eclipse, split = load_best_eclipse(h_results, seed, args)
            all_train_data = split["train"]
            f_eclipse, _ = load_best_eclipse(f_results, seed, args)
            for size in batch_sizes:
                train_data = all_train_data[:size * 50]
                for i in trange(0, len(train_data), size):
                    start_time = time.time()
                    _ = h_eclipse.predict(train_data[i: i+size])
                    end_time = time.time() - start_time
                    times["H eclipse"][str(size)].append(end_time)
                    start_time = time.time()
                    _ = f_eclipse.predict(train_data[i: i+size])
                    end_time = time.time() - start_time
                    times["F eclipse"][str(size)].append(end_time)
        with open(runtime_path, "w") as r_file:
            json.dump(times, r_file)
    else:
        with open(runtime_path) as r_file:
            times = json.load(r_file)
        batch_sizes = [int(b) for b in times["H eclipse"].keys()]
    if os.path.exists(bec_path := f"results/BECPred/runtimes.json"):
        with open(bec_path) as r_file:
            bec_runtime = json.load(r_file)
        times.update(bec_runtime)

    # Plot the runtime
    f, ax = plt.subplots(1, 1, sharey=True, facecolor='w', figsize=(10, 7))
    colours = mpl.colormaps['Set1']
    box_width = 0.25  # width of each boxplot
    positions = []
    for i in range(len(batch_sizes)):
        positions.append([i - box_width, i, i + box_width])

    for i, (key, value) in enumerate(times.items()):
        line_props = dict(color=colours[i], linewidth=2)
        ax.boxplot([value[str(b)] for b in batch_sizes], vert=False, positions=[p[i] for p in positions], widths=box_width, patch_artist=False,
                   boxprops=line_props, whiskerprops=line_props, capprops=line_props, medianprops=line_props,
                   flierprops=dict(marker='o', markeredgecolor=colours[i], markersize=5), label=key, showfliers=False)

    ax.set_xscale('log', base=2)
    # Add labels and title
    ax.set_xlabel('Runtime (Seconds, Log2 Scale)', fontsize=18)
    ax.set_ylabel('Batch Sizes', fontsize=18)
    ax.set_yticks(range(len(batch_sizes)), [str(b) for b in batch_sizes], fontsize=16)

    ax.tick_params(axis="x", labelsize=16)
    ax.axhline(0.45, linestyle='--', color='gray', linewidth=1)
    ax.axhline(1.55, linestyle='--', color='gray', linewidth=1)
    ax.axhline(2.5, linestyle='--', color='gray', linewidth=1)

    # Add legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(list(reversed(handles)), list(reversed(labels)), fontsize=17, framealpha=1, loc="center right")
    plt.tight_layout()
    plt.savefig("results/summary/eclipse_runtimes.pdf", dpi=200)


def runtime_main():
    arguments = get_arguments()
    runtime_analysis(arguments)


if __name__ == "__main__":
    # Figure 3
    runtime_main()
