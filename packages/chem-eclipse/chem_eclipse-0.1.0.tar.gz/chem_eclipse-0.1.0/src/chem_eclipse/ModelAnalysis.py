from chem_eclipse.utils import *
from rdkit.Chem.Draw import rdMolDraw2D
import json
import os
import shutil
from copy import deepcopy
import numpy as np
from joblib import Parallel, delayed
from tqdm import tqdm
import plotly.express as px
import pandas as pd
from collections import defaultdict


def plot_bursts():
    enzymes = pd.read_csv("data/ecmap.csv")
    enzymes = enzymes.drop_duplicates(subset=["rdkit_reaction"])
    enzymes = list(enzymes.ec_num)
    enzyme_sunburst(enzymes, "ecmap_ec")
    enzymes = pd.read_csv("data/envipath.csv")
    enzymes = enzymes[enzymes["dataset"] == "bbd"]
    enzymes = enzymes.dropna(subset=["ec_num"])
    enzymes = enzymes.drop_duplicates(subset=["rdkit_reaction"])
    enzymes = list(enzymes.ec_num)
    enzyme_sunburst(enzymes, "envipath_ec")


def enzyme_sunburst(enzymes, filename):
    records = []
    skipped = 0
    for ec in enzymes:
        parts = ec.split(".")
        if len(parts) >= 3:
            records.append({
                "level1": parts[0],
                "level2": f"{parts[0]}.{parts[1]}",
                "level3": f"{parts[0]}.{parts[1]}.{parts[2]}"
            })
        else:
            skipped += 1
    print(f"Skipped {skipped} as they had less than 3 levels.")
    df = pd.DataFrame(records)
    # Count occurrences
    counts = df.groupby(["level1", "level2", "level3"]).size().reset_index(name='count')
    # Parameters
    top_n_level2 = 3  # Top level 2 per EC class
    top_n_level3 = 3  # Top level 3 per level 2

    # Find top N level2 per level1
    top_level2 = (
        counts.groupby(["level1", "level2"])["count"].sum()
        .groupby(level=0, group_keys=False)
        .nlargest(top_n_level2)
        .reset_index()[["level1", "level2"]]
    )

    # Label level2 as '-' where not in top
    def label_level2(row):
        if (row["level1"], row["level2"]) in top_level2.itertuples(index=False, name=None):
            return row["level2"]
        return f"{row['level1']}.-"

    counts["level2_mod"] = counts.apply(label_level2, axis=1)

    # Find top N level3 per level2_mod
    counts["level2_group"] = counts["level2_mod"]  # for grouping level3

    top_level3 = counts.groupby(["level2_group", "level3"])["count"].sum().groupby(level=0, group_keys=False).nlargest(
        top_n_level3).reset_index()[["level2_group", "level3"]]

    # Label level3 as 'Other' where not in top
    def label_level3(row):
        if (row["level2_group"], row["level3"]) in top_level3.itertuples(index=False, name=None):
            return row["level3"]
        return f"{row['level2_group']}.-"

    counts["level3_mod"] = counts.apply(label_level3, axis=1)

    # Aggregate modified tree
    agg = (counts.groupby(["level1", "level2_mod", "level3_mod"])["count"].sum().reset_index())

    # Plot sunburst
    fig = px.sunburst(
        agg,
        path=["level1", "level2_mod", "level3_mod"],
        values="count",
        color="level1",  # use top-level EC class for coloring
        color_discrete_map={
            "1": "#1f77b4",  # blue
            "2": "#2ca02c",  # green
            "3": "#d62728",  # red
            "4": "#9467bd",  # purple
            "5": "#8c564b",  # brown
            "6": "#e377c2",  # pink
            "Other": "#7f7f7f"  # optional default/fallback
        }
    )
    fig.update_traces(insidetextfont=dict(size=50))
    fig.update_layout(margin=dict(t=0, l=0, r=-0, b=5))
    fig.write_image(f"results/summary/{filename}.pdf", width=1000, height=1000)
    return


def calculate_mean_eclipse(results):
    """
    Given a list of result dictionaries from multiple seeds, where each dictionary
    has the format {threshold: {"recall": x, "precision": y, "f1": z}}, compute
    the mean and std of each metric at each threshold.

    Output format:
    {
        "precision": {
            "0.1": {"mean": ..., "std": ...},
            ...
        },
        "recall": {
            ...
        },
        "f1": {
            ...
        }
    }
    """
    thresholds = results[0].keys()
    metrics = results[0][next(iter(thresholds))].keys()

    mean_std = {}

    for threshold in thresholds:
        for metric in metrics:
            if metric == "predictions":
                continue
            values = [run[threshold][metric] for run in results]
            mean = np.mean(values)
            std = np.std(values)
            mean_std.setdefault(metric, {})[threshold] = {"mean": mean, "std": std}

    return mean_std


def forest_eclipse_comp():
    base_path = "results/ECLIPSEModel"
    paths = os.listdir(base_path)
    all_results = {}
    for path in tqdm(paths):
        config = "_".join(path.split("_")[:-1])
        with open(os.path.join(base_path, path, "val_output.json")) as r_file:
            results = json.load(r_file)
        for result in results:
            del results[result]["predictions"]
        all_results.setdefault(config, []).append(results)

    rows = []
    for config, results in tqdm(all_results.items()):
        with open(os.path.join(base_path, f"{config}_0", "config.json")) as c_file:
            config_dict = json.load(c_file)
        config_dict.pop("seed", None)
        mean_std = calculate_mean_eclipse(results)
        recall, precision, _ = sort_recall_precision({float(tolerance): recall["mean"] for tolerance, recall in
                                                      mean_std["recall"].items()},
                                                     {float(tolerance): precision["mean"] for tolerance, precision in
                                                      mean_std["precision"].items()})
        recall_err, precision_err, _ = sort_recall_precision({float(tolerance): recall["std"] for tolerance, recall in
                                                              mean_std["recall"].items()},
                                                             {float(tolerance): precision["std"] for
                                                              tolerance, precision in
                                                              mean_std["precision"].items()})
        plot_pr_curve([], [], 0.0, "", path=f"results/summary/pr_{config}.png",
                      extra_pr=[[recall, precision, "eclipse"]], error=[[recall_err, precision_err]])
        for metric, cls_dict in mean_std.items():
            best_tolerance = max(cls_dict, key=lambda x: cls_dict.get(x)["mean"])
            metric_peak = cls_dict[best_tolerance]["mean"]
            metric_peak_std = cls_dict[best_tolerance]["std"]
            row_dict = {
                "config": config,
                "metric": metric,
                "class": "overall",
                "peak_mean": metric_peak,
                "peak_tolerance": best_tolerance,
                "peak_std": metric_peak_std
            }
            row_dict.update(config_dict)
            rows.append(row_dict)

    df = pd.DataFrame(rows)
    df.to_csv("results/summary/eclipse_mean_std.csv", index=False)


def eclipse_per_seed(eclipse_type):
    base_path = "results/ECLIPSEModel"
    os.makedirs("results/summary", exist_ok=True)
    eclipse_type = convert_eclipse_type(eclipse_type)
    if eclipse_type == "hierarchy":
        files = [os.path.join(base_path, f) for f in os.listdir(base_path) if "flat" not in f]
    elif eclipse_type == "flat":
        files = [os.path.join(base_path, f) for f in os.listdir(base_path) if "flat" in f]
    df = process_eclipse(files)
    df.to_csv(f"results/summary/{eclipse_type}.csv", index=False)


def process_eclipse(files):
    results = Parallel(n_jobs=25, batch_size=10)(delayed(parallel_process)(file) for file in tqdm(files))
    all_keys = set()
    for result in results:
        all_keys.update(result.keys())
    results_dict = {}
    for result in results:
        for key in all_keys:
            results_dict.setdefault(key, []).extend(result.get(key, [None] * len(list(result.values())[0])))
    dataframe = pd.DataFrame.from_dict(results_dict)
    print("Built data frame")
    return dataframe


def parallel_process(file):
    results_dict = {}
    with open(os.path.join(file, "config.json")) as c_file:
        config = json.load(c_file)
    config.pop("expand", 0)
    with open(os.path.join(file, "val_tol_output.json")) as r_file:
        val_tol_results = json.load(r_file)
    for v in val_tol_results:
        del val_tol_results[v]["predictions"]
    with open(os.path.join(file, "test_tol_output.json")) as r_file:
        test_tol_results = json.load(r_file)
    for v in test_tol_results:
        del test_tol_results[v]["predictions"]

    tolerances = set(val_tol_results.keys()) | set(test_tol_results.keys())
    for tolerance in tolerances:
        dicts = []
        if tolerance in val_tol_results and tolerance in test_tol_results:
            dicts.append((val_tol_results, test_tol_results, "tolerance"))
        for val_dict, test_dict, thresh_type in dicts:
            for key in config:
                results_dict.setdefault(key, []).append(config[key])
            results_dict.setdefault("path", []).append(file)
            results_dict.setdefault("tolerance", []).append(tolerance)
            results_dict.setdefault("val_f1", []).append(val_dict[tolerance]["f1"])
            results_dict.setdefault("val_recall", []).append(val_dict[tolerance]["recall"])
            results_dict.setdefault("val_precision", []).append(val_dict[tolerance]["precision"])
            results_dict.setdefault("thresh_type", []).append(thresh_type)
            for metric, value in test_dict[tolerance].items():
                if metric != "predictions":
                    results_dict.setdefault(metric, []).append(value)
    return results_dict


def BECPred_analysis():
    base_path = "results/BECPred"
    files = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    results_dict = {"seed": [], "dataset": [], "path": []}
    for file in tqdm(files):
        if "bbd" in file:
            dataset = "bbd"
        else:
            dataset = "ecmap"
        seed = file.split("_")[1]
        with open(f"data/eclipse_kfold/{dataset}_3_40/{seed}.json") as s_file:
            split = json.load(s_file)
        i_to_ec = {i: ec for ec, i in split["ec_to_i"].items()}
        results_dict["seed"].append(int(seed))
        results_dict["dataset"].append(dataset)
        results_dict["path"].append(os.path.join(base_path, file))
        with open(os.path.join(base_path, file, "test_results.json")) as r_file:
            results = json.load(r_file)["model_outputs"]
        results = np.array(results)
        pred_ids = np.argmax(results, axis=-1)
        test_one_hot = np.array(split["e_test"])
        true_ec = one_hots_to_hierarchies(split["e_test"], i_to_ec)
        pred_ec = np.zeros((test_one_hot.shape[0], len(i_to_ec)), dtype=np.bool_)

        offset_i = 0
        for i, one_hot in enumerate(test_one_hot):
            num_true = len(np.nonzero(one_hot)[0])
            for j in range(num_true):
                pred_ec[i, pred_ids[i + offset_i]] = True
                offset_i += 1
            offset_i -= 1

        pred_ec = one_hots_to_hierarchies(pred_ec, i_to_ec)
        metrics = hierarchy_eclipse_eval(split["test"], true_ec, pred_ec)
        with open(os.path.join(base_path, file, "formatted_test_results.json"), "w") as r_file:
            json.dump(metrics, r_file)
        del metrics["predictions"]
        for key, value in metrics.items():
            results_dict.setdefault(key, []).append(value)
    dataframe = pd.DataFrame.from_dict(results_dict)
    dataframe.to_csv("results/summary/bec_pred.csv", index=False)


def all_eclipse_results(dataset="ecmap"):
    hierarchy = pd.read_csv("results/summary/hierarchy.csv")
    hierarchy = hierarchy[hierarchy["data_name"] == dataset]
    flat = pd.read_csv("results/summary/flat.csv")
    flat = flat[flat["data_name"] == dataset]

    inner_dict = {"H Recall": [], "H Precision": [], "H F1": []}
    inner_dict.update({f"L{i} Recall": [] for i in range(1, 4)})
    inner_dict.update({f"L{i} Precision": [] for i in range(1, 4)})
    inner_dict.update({f"L{i} F1": [] for i in range(1, 4)})
    method_stats = {"F-eclipse": deepcopy(inner_dict),
                    "H-eclipse": deepcopy(inner_dict)}
    bec_exists = os.path.exists(bec_path := "results/summary/bec_pred.csv")
    if bec_exists:
        bec_pred = pd.read_csv(bec_path)
        bec_pred = bec_pred[bec_pred["dataset"] == dataset]
        method_stats["BECPred"] = deepcopy(inner_dict)
        for _, row in bec_pred.iterrows():
            method_stats["BECPred"]["H Recall"].append(row["recall"])
            method_stats["BECPred"]["H Precision"].append(row["precision"])
            method_stats["BECPred"]["H F1"].append(row["f1"])
            for i in range(1, 4):
                method_stats["BECPred"][f"L{i} Recall"].append(row[f"{i}_recall"])
                method_stats["BECPred"][f"L{i} Precision"].append(row[f"{i}_precision"])
                method_stats["BECPred"][f"L{i} F1"].append(row[f"{i}_f1"])

    for seed, group in hierarchy.groupby("seed"):
        row = group.loc[group["val_f1"].idxmax()]
        print(row["thresh_type"])
        shutil.copytree(row.path, f"results/summary/best_hierarchy/{os.path.basename(row.path)}", dirs_exist_ok=True)
        method_stats["H-eclipse"]["H Recall"].append(row["recall"])
        method_stats["H-eclipse"]["H Precision"].append(row["precision"])
        method_stats["H-eclipse"]["H F1"].append(row["f1"])
        for i in range(1, 4):
            method_stats["H-eclipse"][f"L{i} Recall"].append(row[f"{i}_recall"])
            method_stats["H-eclipse"][f"L{i} Precision"].append(row[f"{i}_precision"])
            method_stats["H-eclipse"][f"L{i} F1"].append(row[f"{i}_f1"])

    for seed, group in flat.groupby("seed"):
        row = group.loc[group["val_f1"].idxmax()]
        print(row["thresh_type"])
        shutil.copytree(row.path, f"results/summary/best_flat/{os.path.basename(row.path)}", dirs_exist_ok=True)
        method_stats["F-eclipse"]["H Recall"].append(row["recall"])
        method_stats["F-eclipse"]["H Precision"].append(row["precision"])
        method_stats["F-eclipse"]["H F1"].append(row["f1"])
        for i in range(1, 4):
            method_stats["F-eclipse"][f"L{i} Recall"].append(row[f"{i}_recall"])
            method_stats["F-eclipse"][f"L{i} Precision"].append(row[f"{i}_precision"])
            method_stats["F-eclipse"][f"L{i} F1"].append(row[f"{i}_f1"])

    # Compute mean ± std and format
    rows = []
    for method, metrics in method_stats.items():
        for metric, values in metrics.items():
            mean = np.mean(values)
            std = np.std(values)
            level, metric_type = metric.split(" ", 1)  # e.g. "L1 Recall" → ("L1", "Recall")
            rows.append({
                "Level": level,
                "Metric": metric_type,
                "Method": method,
                "Value": f"{mean:.2%} ± {std * 100:.2f}"
            })

    df = pd.DataFrame(rows)
    # Pivot to get methods as columns
    df_pivot = df.pivot_table(index=["Level", "Metric"], columns="Method", values="Value", aggfunc="first")
    latex_table = df_pivot.to_latex(escape=False, column_format="ccccc", multirow=True)
    latex_table = latex_table.replace("%", r"\%")
    print(f"eclipse results for {dataset}")
    print(latex_table)


def eclipse_l1_breakdown(dataset="ecmap"):
    inner_dict = {str(ec): {"H Recall": [], "H Precision": [], "H F1": []} for ec in range(1, 8)}
    method_stats = {"F-eclipse": deepcopy(inner_dict),
                    "H-eclipse": deepcopy(inner_dict)}
    hierarchy = pd.read_csv("results/summary/hierarchy.csv")
    hierarchy = hierarchy[hierarchy["data_name"] == dataset]
    flat = pd.read_csv("results/summary/flat.csv")
    flat = flat[flat["data_name"] == dataset]
    bec_exists = os.path.exists(bec_path := "results/summary/bec_pred.csv")
    if bec_exists:
        method_stats["BECPred"] = deepcopy(inner_dict)
        bec_pred = pd.read_csv(bec_path)
        bec_pred = bec_pred[bec_pred["dataset"] == dataset]
        for seed, group in bec_pred.groupby("seed"):
            row = group.iloc[0]
            bec_eclipse = group_becpred_l1(row)
            for ec, result in bec_eclipse.items():
                method_stats["BECPred"][ec]["H Recall"].append(result["recall"])
                method_stats["BECPred"][ec]["H Precision"].append(result["precision"])
                method_stats["BECPred"][ec]["H F1"].append(result["f1"])

    for seed, group in hierarchy.groupby("seed"):
        row = group.loc[group["val_f1"].idxmax()]
        h_eclipse = group_eclipse_l1(row)
        for ec, result in h_eclipse.items():
            method_stats["H-eclipse"][ec]["H Recall"].append(result["recall"])
            method_stats["H-eclipse"][ec]["H Precision"].append(result["precision"])
            method_stats["H-eclipse"][ec]["H F1"].append(result["f1"])

    for seed, group in flat.groupby("seed"):
        row = group.loc[group["val_f1"].idxmax()]
        f_eclipse = group_eclipse_l1(row)
        for ec, result in f_eclipse.items():
            method_stats["F-eclipse"][ec]["H Recall"].append(result["recall"])
            method_stats["F-eclipse"][ec]["H Precision"].append(result["precision"])
            method_stats["F-eclipse"][ec]["H F1"].append(result["f1"])

    # --- Convert to long DataFrame ---
    records = []
    for method, ec_dict in method_stats.items():
        for ec, metrics in ec_dict.items():
            for metric_name, values in metrics.items():
                mean = np.mean(values) if values else np.nan
                std = np.std(values) if values else np.nan
                records.append({
                    "EC": ec,
                    "Metric": metric_name.split()[-1],  # Recall / Precision / F1
                    "Method": method,
                    "Value": f"{mean:.2%} ± {std * 100:.2f}"
                })

    df = pd.DataFrame(records)

    # --- Pivot so methods are columns ---
    df_pivot = df.pivot(index=["EC", "Metric"], columns="Method", values="Value")

    # --- Export to LaTeX with multirow ---
    latex_table = df_pivot.to_latex(escape=False, multicolumn=True, multirow=True, column_format="cc|ccc")
    latex_table = latex_table.replace("%", r"\%")
    print(f"eclipse EC level one breakdown for {dataset}")
    print(latex_table)


def group_becpred_l1(row):
    with open(os.path.join(row.path, "formatted_test_results.json")) as r_file:
        test_results = json.load(r_file)
    by_ec = {}
    for ec_dict in test_results["predictions"]:
        true, pred, smiles = ec_dict["true"], ec_dict["pred"], ec_dict["smiles"]
        for t in true:
            ec1 = t.split(".")[0]
            by_ec.setdefault(ec1, []).append(ec_dict)
    ec_results = {ec: run_metrics(dicts) for ec, dicts in by_ec.items()}
    return ec_results


def run_metrics(dicts):
    smiles, true, pred = [], [], []
    for i, row in enumerate(dicts):
        smil, tp, pp = row["smiles"], row["true"], row["pred"]
        smiles.append(smil)
        true.append([[".".join(t.split(".")[:i]) for i in range(1, len(t.split(".")) + 1)] for t in tp])
        pred.append([[".".join(t.split(".")[:i]) for i in range(1, len(t.split(".")) + 1)] for t in pp])
    m = hierarchy_eclipse_eval(smiles, true, pred)
    return m


def group_eclipse_l1(row):
    file = row.path
    with open(os.path.join(file, "test_tol_output.json")) as r_file:
        test_results = json.load(r_file)
    test_results = test_results[str(row.tolerance)]

    by_ec = {}
    for ec_dict in test_results["predictions"]:
        true, pred, smiles = ec_dict["true"], ec_dict["pred"], ec_dict["smiles"]
        for t in true:
            ec1 = t.split(".")[0]
            by_ec.setdefault(ec1, []).append(ec_dict)
    ec_results = {ec: run_metrics(dicts) for ec, dicts in by_ec.items()}
    return ec_results


def load_reaction_to_ec(split_path):
    """Build mapping substrate SMILES -> EC number from split file."""
    with open(split_path) as f:
        split = json.load(f)

    mapping = {}
    for set_name in ["train", "val", "test"]:
        reactions = split[set_name]
        enzymes = split[f"e_{set_name}"]
        for rxn, ec in zip(reactions, enzymes):
            if ">>" not in rxn:
                continue
            substrate, _ = rxn.split(">>", 1)
            mapping.setdefault(substrate, []).append(ec)
    return mapping


def group_predictions_by_ec(test_output, reaction_to_ec):
    """Group test predictions by Level-1 EC number."""
    grouped = {}
    for substrate, entry in test_output.items():
        ecs = reaction_to_ec.get(substrate)
        for ec in ecs:
            ec1 = ec.split(".")[0]
            grouped.setdefault(ec1, {})[substrate] = entry
    return grouped


def enzyme_mean_dicts(dicts):
    metrics = {}

    # Collect values
    for d in dicts:
        for key, values in d.items():
            if "predictions" in key:  # skip
                continue
            metrics.setdefault(key, {})
            if isinstance(values, dict):  # e.g., recall, precision, accuracy dict
                for subkey, val in values.items():
                    metrics[key].setdefault(subkey, [])
                    metrics[key][subkey].append(val)
            else:  # plain scalar
                metrics[key].setdefault("scalar", [])
                metrics[key]["scalar"].append(values)

    # Compute mean/std and flatten
    result = {}
    for key, subdict in metrics.items():
        result.setdefault(key, {})
        for subkey, vals in subdict.items():
            arr = np.array(vals, dtype=float)
            result[key][f"{subkey}_mean"] = arr.mean()
            result[key][f"{subkey}_std"] = arr.std(ddof=1) if len(arr) > 1 else 0.0

    return result


def get_plot_format(mean_dict, title):
    recall, precision, _, order = sort_recall_precision({k: v for k, v in mean_dict["recall"].items() if "mean" in k},
                                                        {k: v for k, v in mean_dict["precision"].items() if "mean" in k},
                                                        return_order=True)
    r_error = [mean_dict["recall"][k.replace("_mean", "_std")] for k in order]
    p_error = [mean_dict["precision"][k.replace("_mean", "_std")] for k in order]
    return [recall, precision, title], [r_error, p_error]


def prediction_subset_analysis(subset):
    test_reactions = []
    predictions = []
    probabilities = []
    for reactant in subset:
        actual_products = subset[reactant]["actual"]
        for product in actual_products:
            test_reactions.append(f"{reactant}>>{product}")
            predictions.append(subset[reactant]["predict"])
            probabilities.append(subset[reactant]["scores"])
    return process_compare_reactions(test_reactions, (predictions, probabilities), get_thresholds(value_type=set))


def product_results(dataset="ecmap"):
    base_path = "results/ECLIPSEProdModel/"
    files = {}
    for f in os.listdir(base_path):
        if "tree" in f and dataset in f.split("_")[0]:
            seed = f.split("_")[5]
            enzyme = f.split("_")[-1]
            enzyme = False if enzyme == "false" else True
            files.setdefault(seed, {})[enzyme] = f
    true_mean, pred_mean, no_mean = [], [], []
    per_enzyme_mean = {}
    for seed, file in files.items():
        enzyme_folder = file[True]
        no_enzyme_folder = file[False]
        with open(os.path.join(base_path, enzyme_folder, "test_output_enzyme.json")) as r_file:
            true_e_results = json.load(r_file)
        with open(os.path.join(base_path, enzyme_folder, "test_output_no_enzyme.json")) as r_file:
            pred_e_results = json.load(r_file)
        with open(os.path.join(base_path, no_enzyme_folder, "test_output_enzyme.json")) as r_file:
            no_e_results = json.load(r_file)
        reaction_to_e = load_reaction_to_ec(os.path.join(base_path, enzyme_folder, f"split_{dataset}.json"))
        true_grouped = group_predictions_by_ec(true_e_results["predictions"], reaction_to_e)
        pred_grouped = group_predictions_by_ec(pred_e_results["predictions"], reaction_to_e)
        no_grouped = group_predictions_by_ec(no_e_results["predictions"], reaction_to_e)
        for ec in true_grouped:
            per_enzyme_mean.setdefault(ec, [[], [], []])
            per_enzyme_mean[ec][0].append(prediction_subset_analysis(true_grouped[ec]))
            per_enzyme_mean[ec][1].append(prediction_subset_analysis(pred_grouped[ec]))
            per_enzyme_mean[ec][2].append(prediction_subset_analysis(no_grouped[ec]))
        true_mean.append(true_e_results)
        pred_mean.append(pred_e_results)
        no_mean.append(no_e_results)
    true_mean = enzyme_mean_dicts(true_mean)
    pred_mean = enzyme_mean_dicts(pred_mean)
    no_mean = enzyme_mean_dicts(no_mean)
    for ec in per_enzyme_mean:
        true_mean_ec = enzyme_mean_dicts(per_enzyme_mean[ec][0])
        pred_mean_ec = enzyme_mean_dicts(per_enzyme_mean[ec][1])
        no_mean_ec = enzyme_mean_dicts(per_enzyme_mean[ec][2])
        print(f"Table for {dataset} EC {ec}")
        plot_pr_print_table(true_mean_ec, pred_mean_ec, no_mean_ec, f"{dataset}_{ec}")
    print(f"Overall table for {dataset}")
    plot_pr_print_table(true_mean, pred_mean, no_mean, dataset)


def plot_pr_print_table(true_mean, pred_mean, no_mean, dataset):
    # Plot the PR curve
    if "soil" in dataset or "sludge" in dataset:
        true_r_p = get_plot_format(true_mean, "Pred EC")
    else:
        true_r_p = get_plot_format(true_mean, "True EC")
    pred_r_p = get_plot_format(pred_mean, "Pred EC")
    no_r_p = get_plot_format(no_mean, "No EC")
    if "soil" in dataset or "sludge" in dataset:
        plot_pr_curve([], [], 0, "", f"results/summary/{dataset}_product.pdf",
                      extra_pr=[no_r_p[0], true_r_p[0]], error=[no_r_p[1], true_r_p[1]],
                      usetex=True)
    else:
        plot_pr_curve([], [], 0, "", f"results/summary/{dataset}_product.pdf",
                      extra_pr=[no_r_p[0], pred_r_p[0], true_r_p[0]], error=[no_r_p[1], pred_r_p[1], true_r_p[1]],
                      usetex=True, legend_loc="upper right" if "bbd" in dataset else "lower left")

    # Create the Top-K table
    acc_keys = sorted(set(k.rsplit("_", 1)[0] for k in true_mean["accuracy"].keys() if k.endswith("_mean")), key=lambda x: int(x.split("_")[-1]))
    acc_keys = acc_keys[:3]

    data = {}
    if "soil" in dataset or "sludge" in dataset:
        groups = [("Pred EC", true_mean), ("No EC", no_mean)]
    else:
        groups = [("True EC", true_mean), ("Pred EC", pred_mean), ("No EC", no_mean)]
    for label, mean_dict in groups:
        col = []
        for acc in acc_keys:
            mean = mean_dict["accuracy"].get(f"{acc}_mean", float("nan"))
            std = mean_dict["accuracy"].get(f"{acc}_std", float("nan"))
            col.append(f"{mean:.2%} ± {std * 100:.2f}")
        data[label] = col

    df = pd.DataFrame(data, index=[k.replace("_", "-") for k in acc_keys])
    latex_table = df.to_latex(escape=False, column_format="c|ccc",
                              caption="Top-K accuracy comparison across True EC, Pred EC, and No EC models.",
                              label="tab:topk_accuracy")
    latex_table = latex_table.replace("%", r"\%")
    print(latex_table)


def best_hierarchy_configs(dataset):
    results = pd.read_csv("results/summary/hierarchy.csv")
    results = results[results["data_name"] == dataset]
    configs = {"Estimators": [], "Max Depth": [], "Tolerance": [], "Fold": []}
    for fold, group in results.groupby("seed"):
        best_row = group.loc[group["val_f1"].idxmax()]
        configs["Estimators"].append(best_row.n_estimators)
        configs["Max Depth"].append(best_row.max_depth)
        configs["Tolerance"].append(f"{best_row.tolerance:.3f}")
        configs["Fold"].append(fold)
    dataframe = pd.DataFrame.from_dict(configs)
    dataframe = dataframe.sort_values(by="Fold")
    latex_table = dataframe.to_latex(escape=False, column_format="cccc", index=False)
    print(f"Best hierarchy configs for each seed on {dataset}")
    print(latex_table)


def best_flat_configs(dataset):
    results = pd.read_csv("results/summary/flat.csv")
    results = results[results["data_name"] == dataset]
    configs = {"Estimators": [], "Max Depth": [], "Num Chains": [], "Tolerance": [], "Fold": []}
    for fold, group in results.groupby("seed"):
        best_row = group.loc[group["val_f1"].idxmax()]
        configs["Estimators"].append(best_row.n_estimators)
        configs["Max Depth"].append(best_row.max_depth)
        configs["Tolerance"].append(f"{best_row.tolerance:.3f}")
        configs["Num Chains"].append(best_row.n_chains)
        configs["Fold"].append(fold)
    dataframe = pd.DataFrame.from_dict(configs)
    dataframe = dataframe.sort_values(by="Fold")
    latex_table = dataframe.to_latex(escape=False, column_format="ccccc", index=False)
    print(f"Best flat configs for each seed on {dataset}")
    print(latex_table)


def inference_distribution(train_data="ecmap", dataset="soil"):
    os.makedirs("results/summary", exist_ok=True)
    if dataset != "bbd" and os.path.exists("results/summary/bbd_final"):
        with open(f"results/summary/bbd_final/{dataset}_pred.json") as i_file:
            p_from_bbd = json.load(i_file)
        from_bbd_e = []
        for p in p_from_bbd:
            from_bbd_e.extend(p[1])
        enzyme_sunburst(from_bbd_e, f"{dataset}_pred_from_bbd")
    with open(f"results/summary/{train_data}_final/{dataset}_pred.json") as i_file:
        p_from_ecmap = json.load(i_file)

    from_ecmap_e = []
    for p in p_from_ecmap:
        from_ecmap_e.extend(p[1])
    enzyme_sunburst(from_ecmap_e, f"{dataset}_pred_from_{train_data}")
    if not os.path.exists(pred_path := "data/envipath_pred_ec.csv"):
        data_frame = pd.read_csv("data/envipath.csv")
        data_frame[["rdkit_reactants", "rdkit_products"]] = data_frame["rdkit_reaction"].str.split(">>", n=1, expand=True)
        data_frame["pred_ec"] = [pd.NA for _ in range(len(data_frame))]
    else:
        data_frame = pd.read_csv(pred_path)
    reactant_to_ec = defaultdict(set)
    for p in p_from_ecmap:
        reactant_to_ec[p[0]].update(p[1])
    value_lengths = pd.Series([len(v) for v in reactant_to_ec.values() if len(v) > 1])
    print(value_lengths.describe())
    reactant_to_ec = {k: v.pop() for k, v in reactant_to_ec.items()}
    mask = data_frame["dataset"] == dataset
    data_frame.loc[mask, "pred_ec"] = data_frame.loc[mask, "rdkit_reactants"].map(reactant_to_ec)
    data_frame.to_csv(pred_path, index=False)


def inference_performance():
    true = pd.read_csv("data/enviPath_EC_Rhea_mapping.csv")
    true = true.dropna(subset="EC number from Rhea")
    datasets = ['soil', 'sludge']
    for dataset in datasets:
        base_path = "results/summary/ecmap_final"
        best_model = [f for f in os.listdir(base_path) if "final" in f][0]
        with open(os.path.join(base_path, best_model, "split.json")) as s_file:
            ec_to_i = json.load(s_file)["ec_to_i"]
        if dataset == "soil":
            sub_true = true[true["Package"] == "EAWAG-SOIL"]
            with open("results/summary/ecmap_final/soil_pred.json") as p_file:
                pred = json.load(p_file)
            with open("data/envipath/soil.json") as o_file:
                original = json.load(o_file)['reactions']
        elif dataset == "sludge":
            sub_true = true[true["Package"] == "EAWAG-SLUDGE"]
            with open("results/summary/ecmap_final/sludge_pred.json") as p_file:
                pred = json.load(p_file)
            with open("data/envipath/sludge.json") as o_file:
                original = json.load(o_file)['reactions']
        else:
            raise ValueError(f"Unknown dataset {dataset}")
        pred_dict = {p[0]: p[1] for p in pred}
        true_dict = {}
        url_to_r = {r['id']: r for r in original}
        for _, row in sub_true.iterrows():
            reaction = url_to_r.get(row['enviPath reaction URL'])
            if reaction:
                smirks = canon_smirk(reaction['smirks'], canon_smile_rdkit)
                reactant, _ = smirks.split(">>")[:2]
                if reactant not in true_dict:
                    true_dict[reactant] = []
                ec = ".".join(row["EC number from Rhea"].split(".")[:3])
                pos = 3
                while ec not in ec_to_i and pos > 0:
                    ec = ec.split(".")
                    ec[pos := pos - 1] = "-"
                    ec = ".".join(ec)
                if ec == "-.-.-":
                    continue
                if ec not in true_dict[reactant]:
                    true_dict[reactant].append(ec)
        print(f"There are {len(true_dict)} true examples for {dataset}")
        smiles, true_ec, pred_ec = [], [], []
        for s, ec in true_dict.items():
            smiles.append(s)
            true_ec.append([[".".join(t.split(".")[:i]) for i in range(1, len(t.split(".")) + 1)] for t in ec])
            pred_ec.append([[".".join(t.split(".")[:i]) for i in range(1, len(t.split(".")) + 1)] for t in pred_dict[s]])
        metrics = hierarchy_eclipse_eval(smiles, true_ec, pred_ec)
        print(f"Metrics for {dataset}: {metrics}")


def plot_ec_comparison(smiles, true_ec, pred_ec, figsize=(5, 5), mol_size=(1000, 550), bond_line_width=15, name=""):
    """
    Draws a molecule from a SMILES string and displays true vs predicted EC numbers.
    Uses RDKit's vector drawer to adjust molecule size and line thickness.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("Invalid SMILES string provided.")

    # Prepare molecule for drawing
    Chem.rdDepictor.Compute2DCoords(mol)
    drawer = rdMolDraw2D.MolDraw2DSVG(mol_size[0], mol_size[1])
    options = drawer.drawOptions()
    options.bondLineWidth = bond_line_width  # thickness of bonds
    options.fixedBondLength = 0             # controls scaling (bigger = smaller molecule)
    options.padding = 0.0                   # small border
    options.addAtomIndices = False
    options.minFontSize = 38
    options.addStereoAnnotation = False

    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    mol_svg = drawer.GetDrawingText()

    # Display with matplotlib (vector, not raster)
    plt.rcParams.update({"text.usetex": True})
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis("off")

    # Display the SVG molecule
    from matplotlib.offsetbox import AnnotationBbox, OffsetImage
    import io
    from PIL import Image
    import cairosvg

    # Convert SVG to PNG (still sharp if dpi is high)
    png_data = cairosvg.svg2png(bytestring=mol_svg.encode("utf-8"), dpi=300)
    mol_img = Image.open(io.BytesIO(png_data))
    # Convert to RGBA if not already
    mol_img = mol_img.convert("RGBA")

    # Get bounding box of non-transparent pixels
    bbox = mol_img.getbbox()
    mol_img = mol_img.crop(bbox)
    ax.imshow(mol_img, interpolation=None)

    # Create text block for ECs
    true_text = "\n".join(true_ec) if true_ec else "—"
    pred_text = "\n".join(pred_ec) if pred_ec else "—"

    # Position text (closer to molecule)
    y_offset = -0.05
    ax.text(0.15, y_offset, r"\textbf{True EC}", ha='center', va='top', fontsize=20, fontweight='bold', transform=ax.transAxes)
    ax.text(0.75, y_offset, r"\textbf{Predicted EC}", ha='center', va='top', fontsize=20, fontweight='bold',
            transform=ax.transAxes)

    ax.text(0.15, y_offset - 0.15, true_text, ha='center', va='top', fontsize=20, transform=ax.transAxes)
    ax.text(0.75, y_offset - 0.15, pred_text, ha='center', va='top', fontsize=20, transform=ax.transAxes)

    plt.tight_layout()
    plt.savefig(f"results/summary/example_ec_{name}.pdf", dpi=300, bbox_inches="tight", pad_inches=0)


def recreate_tables_figures():
    """
    # Figure 1
    plot_bursts()
    # Table 3
    best_flat_configs("ecmap")
    best_hierarchy_configs("ecmap")
    # Table 4
    all_eclipse_results("ecmap")
    # Table 5
    eclipse_l1_breakdown("ecmap")
    # Table 6, SupFigure 1 and Figure 4
    product_results("ecmap")
    # Table 7
    best_flat_configs("bbd")
    best_hierarchy_configs("bbd")
    # Table 8
    all_eclipse_results("bbd")
    # Table 9
    eclipse_l1_breakdown("bbd")
    # Table 10
    product_results("bbd")
    # Table 11, SupFigure 2 and Figure 5
    product_results("bbd")
    # Figure 6
    inference_distribution("soil")
    inference_distribution("sludge")
    # Figure 7
    inference_performance()
    plot_ec_comparison("CNC(=O)Oc1cccc2c1OC(C)(C)C2", ['3.5.1'], ['4.1.1', '3.5.1'], name="soil")
    plot_ec_comparison("CC(=O)CC(=O)[O-]", ['1.8.1', '6.4.1', '4.1.1'], ['4.1.1'], name="sludge")
    """
    if os.path.exists("results/BECPred"):
        BECPred_analysis()
    # Figure 1
    plot_bursts()
    # Table 3
    best_flat_configs("ecmap")
    best_hierarchy_configs("ecmap")
    # Table 4
    all_eclipse_results("ecmap")
    # Table 5
    eclipse_l1_breakdown("ecmap")
    # Table 6, SupFigure 1 and Figure 4
    product_results("ecmap")
    # Table 7
    best_flat_configs("bbd")
    best_hierarchy_configs("bbd")
    # Table 8
    all_eclipse_results("bbd")
    # Table 9
    eclipse_l1_breakdown("bbd")
    # Table 10
    product_results("bbd")
    # Table 11, SupFigure 2 and Figure 5
    product_results("bbd")
    # Figure 6
    inference_distribution("soil")
    inference_distribution("sludge")
    # Figure 7
    plot_ec_comparison("CNC(=O)Oc1cccc2c1OC(C)(C)C2", ['3.5.1'], ['4.1.1', '3.5.1'], name="soil")
    plot_ec_comparison("CC(=O)CC(=O)[O-]", ['1.8.1', '6.4.1', '4.1.1'], ['4.1.1'], name="sludge")


if __name__ == "__main__":
    recreate_tables_figures()
