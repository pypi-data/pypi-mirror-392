import copy
import re
from functools import partial
from itertools import product
import numpy as np
import torch
from joblib import Parallel, delayed
from rdkit import RDLogger, Chem
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import precision_recall_fscore_support, auc
from iterstrat.ml_stratifiers import MultilabelStratifiedKFold, MultilabelStratifiedShuffleSplit
from argparse import ArgumentParser
import pandas as pd
import json
from statistics import mean
from chem_eclipse.hiclass import metrics
import matplotlib.pyplot as plt
import os
from enviPath_python.enviPath import enviPath
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader, TensorDataset
from tqdm import tqdm


def hierarchy_eclipse_eval(smiles, true_e, pred_e):
    if not isinstance(true_e, list):
        true_e = true_e.tolist()
    if not isinstance(pred_e, list):
        pred_e = pred_e.tolist()
    depths = []
    depths.extend([max([len(l_1) for l_1 in l]) for l in true_e])
    depth = max(depths)
    num_t = max([len(l) for l in true_e])
    num_p = max([len(l) for l in pred_e])
    num_add = max(num_t, num_p)
    fixed_true = []
    fixed_pred = []
    for true in true_e:
        fixed_true.extend([true + [[""] * depth] * (num_add - len(true))])
    for pred in pred_e:
        fixed_pred.extend([pred + [[""] * depth] * (num_add - len(pred))])
    true_e = np.array(fixed_true)
    pred_e = np.array(fixed_pred)
    true_lvl = [[e for e in ec if e != ""] for ec in true_e[:, :, -1].tolist()]
    pred_lvl = [[e for e in ec if e != ""] for ec in pred_e[:, :, -1].tolist()]
    lvl_dict = {}
    for lvl in range(1, 4):
        t = [list(set(".".join(e.split(".")[:lvl]) for e in ec)) for ec in true_lvl]
        p = [list(set(".".join(e.split(".")[:lvl]) for e in ec)) for ec in pred_lvl]
        mlb = MultiLabelBinarizer()
        y_true_bin = mlb.fit_transform(t)
        y_pred_bin = mlb.transform(p)
        precision, recall, f1, support = precision_recall_fscore_support(y_true_bin, y_pred_bin, average='micro',
                                                                         zero_division=0)
        lvl_dict[f"{lvl}_recall"] = recall
        lvl_dict[f"{lvl}_precision"] = precision
        lvl_dict[f"{lvl}_f1"] = f1

    precision = metrics.precision(true_e, pred_e)
    recall = metrics.recall(true_e, pred_e)
    f1 = metrics.f1(true_e, pred_e)
    predictions = []
    for s, pred, true in zip(smiles, pred_lvl, true_lvl):
        predictions.append({"smiles": s, "pred": pred, "true": true})
    save_dict = {"recall": recall, "precision": precision, "f1": f1, "predictions": predictions}
    save_dict.update(lvl_dict)
    return save_dict


def sort_recall_precision(recall, precision, return_order=False):
    sorted_recall = sorted(recall.items(), key=lambda x: x[1])
    order = [r[0] for r in sorted_recall]
    sorted_recall = np.array([r[1] for r in sorted_recall])
    sorted_precision = np.array([precision[key] for key in order])
    area_under_curve = auc(sorted_recall, sorted_precision)
    if return_order:
        return sorted_recall, sorted_precision, area_under_curve, order
    return sorted_recall, sorted_precision, area_under_curve


def plot_pr_curve(recall, precision, area, data_name, path, file_name=None, extra_pr=None, plot_title=None, **kwargs):
    fig_size = (7, 7)

    # Plot the curve with recall on the x-axis and precision on the y-axis
    plt.figure(figsize=fig_size)
    plt.rcParams.update({"text.usetex": kwargs.get("usetex", False)})
    plt.style.use('seaborn-v0_8-dark-palette')
    if len(recall) > 0:
        plt.plot(recall, precision, label=f'{data_name} (AUC: {area:.4f})')
    colours = ["#000000", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"]
    if extra_pr is not None:
        error = kwargs.get("error", None)
        for i, pr in enumerate(extra_pr):
            plt.plot(pr[0], pr[1], label=pr[2], color=colours[i])
            if error is not None:
                rec_err, prec_err = error[i]

                # Upper bound curve
                upper_recall = np.clip(pr[0] + rec_err, 0, 1)
                upper_prec = np.clip(pr[1] + prec_err, 0, 1)

                # Lower bound curve
                lower_recall = np.clip(pr[0] - rec_err, 0, 1)
                lower_prec = np.clip(pr[1] - prec_err, 0, 1)

                # Build polygon path: go forward on upper, backward on lower
                poly_x = np.concatenate([upper_recall, lower_recall[::-1]])
                poly_y = np.concatenate([upper_prec, lower_prec[::-1]])

                plt.fill(poly_x, poly_y, alpha=0.3, facecolor=colours[i])
    plt.xlim(kwargs.get("xmin", 0), kwargs.get("xlim", 1))
    plt.ylim(kwargs.get("ymin", 0), kwargs.get("ylim", 1))

    # Add labels and title
    plt.xlabel('Recall', fontsize=24)
    plt.xticks(fontsize=24)
    plt.ylabel('Precision', fontsize=24)
    plt.yticks(fontsize=24)

    # Show the legend
    plt.legend(fontsize=22, loc=kwargs.get("legend_loc", "upper right"), framealpha=0.5)
    plt.tight_layout()

    # Show the plot or save it
    if ".png" in path or ".pdf" in path:
        plt.savefig(path, dpi=120)
    else:
        for i in range(1, 100):
            save_loc = f"{path}/precision_recall_{i if file_name is None else file_name}.png"
            if not os.path.exists(save_loc) or file_name is not None:
                plt.savefig(save_loc, dpi=120)
                break
    plt.clf()
    plt.close()
    return


def get_arguments():
    parser = ArgumentParser()
    parser.add_argument("--data-name", type=str, default="ecmap", help="Which dataset to use, bbd, ecmap")
    parser.add_argument("--eclipse-type", type=str, default="h", help="Whether to train the H or F eclipse")
    parser.add_argument("--split-path", type=str, default="",
                        help="Predetermined split file with train, val and test SMILES")
    parser.add_argument("--max-len", type=int, default=380, help="Maximum encoded length to consider")
    parser.add_argument("--min-len", type=int, default=0, help="Minimum encoded length to consider")
    parser.add_argument("--debug", action="store_true", default=False, help="Whether to set parameters for debugging")
    parser.add_argument("--epochs", type=int, default=500, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=128, help="Batch size to target")
    parser.add_argument("--weights-dataset", type=str, default="results/TransformerModel/uspto_rdkit",
                        help="Pretrained weights based on what dataset")
    parser.add_argument("--score-all", action="store_true", help="Whether to group same reactants together")
    parser.add_argument("--folds", type=int, default=10, help="How many folds to use for cross validation, default 10")
    parser.add_argument("--enzymes", action="store_true", help="Whether to also use enzyme data")
    parser.add_argument("--seed", default=0, type=int, help="Seed to use for randomness")
    parser.add_argument("--test", default="", type=str, help="Dataset to use for testing instead of training")
    parser.add_argument("-tm", "--train-many", action="store_true", help="Whether to train many models")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--gpu", action="store_true", help="Whether to use GPU for XGBoost")
    arguments, _ = parser.parse_known_args()
    return arguments


def get_dataset_eclipse(args, test=False):
    if test and args.test:
        data_name = args.test
    else:
        data_name = args.data_name
    if data_name == "ecmap":
        data = pd.read_csv("data/ecmap.csv")
        data = data.drop_duplicates(["rdkit_reactants", "ec_num"])
    elif data_name == "bbd":
        data = pd.read_csv("data/envipath.csv")
        data = data[data["dataset"] == "bbd"]
        data = data.dropna(subset=["ec_num"])
        data = data.drop_duplicates(subset=["rdkit_reactants", "ec_num"])
    elif data_name == "soil" or data_name == "sludge":
        if test:
            data = pd.read_csv("data/envipath.csv")
            data = data[data["dataset"] == data_name]
            data = data.drop_duplicates(subset=["rdkit_reactants"])
        elif os.path.exists(pred_path := "data/envipath_pred_ec.csv"):
            print(f"Warning: EC numbers for {data_name} are predicted")
            data = pd.read_csv(pred_path)
            data = data[data["dataset"] == data_name]
            data = data.drop_duplicates(subset="rdkit_reactants")
            data["ec_num"] = data["pred_ec"]
            data = data.dropna(subset=["ec_num"])
            if len(data) == 0:
                raise RuntimeError(f"There are no predicted enzymes for {data_name}. "
                                   f"Have you run ECLIPSEInference with --test {data_name}?")
        else:
            raise FileNotFoundError(f"Can't find {pred_path} please run ECLIPSEInference.py with --test {data_name}")
    elif os.path.exists(data_name):
        data = pd.read_csv(data_name)
        if not test:
            data = data.dropna(subset=["ec_num"])
            data = data.drop_duplicates(subset=["rdkit_reactants", "ec_num"])
        args.data_name = os.path.basename(data_name).split(".")[0]
    else:
        raise ValueError(f"Unknown dataset or couldn't find file. test={test}: {data_name}")
    return data


def split_eclipse(data_frame, config, args):
    ec_lvl = config.get("ec_lvl", 3)
    ec_min_size = config.get("ec_min", 40)
    splits_path = f"data/eclipse_kfold/{args.data_name}_{ec_lvl}_{ec_min_size}/"
    os.makedirs(splits_path, exist_ok=True)
    if os.path.exists(split_file := os.path.join(splits_path, f"{args.seed}.json")):
        with open(split_file) as s_file:
            return json.load(s_file)

    data_frame["ec_num"] = data_frame["ec_num"].apply(lambda x: ".".join(x.split(".")[:ec_lvl]))
    data_frame["ec_num"] = data_frame["ec_num"].str.replace(".-", "")
    data_frame = data_frame.drop_duplicates(["rdkit_reactants", "ec_num"])

    # START: Algorithm 1 in the paper
    enzyme_dict = {}
    for row in data_frame.itertuples():
        enzyme_dict.setdefault(row.ec_num, set()).add(row.rdkit_reactants)
    ec_pos = ec_lvl
    while any(len(v) < ec_min_size for v in enzyme_dict.values()):
        for key in list(enzyme_dict.keys()):
            value = enzyme_dict[key]
            if len(value) < ec_min_size and len(key.split(".")) >= ec_pos:
                new_key = ".".join(key.split(".")[:ec_pos - 1])
                enzyme_dict.setdefault(new_key, set()).update(value)
                del enzyme_dict[key]
        ec_pos -= 1
        if ec_pos == 0:
            break

    for key in list(enzyme_dict.keys()):
        if len(enzyme_dict[key]) < ec_min_size or len(key) == 0:
            del enzyme_dict[key]
        elif len(k_split := key.split(".")) < ec_lvl:
            k_split.extend(["-"] * (ec_lvl - len(k_split)))
            enzyme_dict[".".join(k_split)] = enzyme_dict.pop(key)
    ec_to_i = {e: i for i, e in enumerate(enzyme_dict.keys())}
    # END

    one_hot = {}
    for e, rs in enzyme_dict.items():
        for r in rs:
            one_hot.setdefault(r, np.zeros(len(ec_to_i), dtype=np.int32))[ec_to_i[e]] = 1
    reactants, enzymes = zip(*one_hot.items())
    reactants, enzymes = np.array(reactants), np.array(enzymes)
    fold_splitter = MultilabelStratifiedKFold(n_splits=10, shuffle=True, random_state=42)
    splits = {}
    for i, (train_ids, test_ids) in enumerate(fold_splitter.split(reactants, enzymes)):
        x_train_val, y_train_val = reactants[train_ids], enzymes[train_ids]
        x_test, y_test = reactants[test_ids], enzymes[test_ids]
        val_splitter = MultilabelStratifiedShuffleSplit(n_splits=1, test_size=len(test_ids), random_state=args.seed)
        train_ids, val_ids = list(val_splitter.split(x_train_val, y_train_val))[0]
        x_train, y_train = x_train_val[train_ids], y_train_val[train_ids]
        x_val, y_val = x_train_val[val_ids], y_train_val[val_ids]
        x_train, y_train, x_val, y_val, x_test, y_test = x_train.tolist(), y_train.tolist(), x_val.tolist(), y_val.tolist(), x_test.tolist(), y_test.tolist()
        splits[i] = {"train": x_train, "val": x_val, "test": x_test, "e_train": y_train, "e_val": y_val, "e_test": y_test, "ec_to_i": ec_to_i}
        with open(os.path.join(splits_path, f"{i}.json"), "w") as f_file:
            json.dump(splits[i], f_file)
    return splits[args.seed]


def expand_search_space(search_space_dict):
    keys = list(search_space_dict.keys())
    values = list(search_space_dict.values())
    return [dict(zip(keys, combo)) for combo in product(*values)]


def split_eclipse_inference(data, config, args, final_train=False):
    data["ec_num"] = data["ec_num"].apply(lambda x: ".".join(x.split(".")[:config["ec_lvl"]]))
    data["ec_num"] = data["ec_num"].str.replace(".-", "")
    data_frame = data.drop_duplicates(["rdkit_reactants", "ec_num"])
    enzyme_dict = {}
    for row in data_frame.itertuples():
        enzyme_dict.setdefault(row.ec_num, set()).add(row.rdkit_reactants)
    ec_pos = config["ec_lvl"]
    while any(len(v) < config["ec_min"] for v in enzyme_dict.values()):
        for key in list(enzyme_dict.keys()):
            value = enzyme_dict[key]
            if len(value) < config["ec_min"] and len(key.split(".")) >= ec_pos:
                new_key = ".".join(key.split(".")[:ec_pos - 1])
                enzyme_dict.setdefault(new_key, set()).update(value)
                del enzyme_dict[key]
        ec_pos -= 1
        if ec_pos == 0:
            break

    for key in list(enzyme_dict.keys()):
        if len(enzyme_dict[key]) < config["ec_min"] or len(key) == 0:
            del enzyme_dict[key]
        elif len(k_split := key.split(".")) < config["ec_lvl"]:
            k_split.extend(["-"] * (config["ec_lvl"] - len(k_split)))
            enzyme_dict[".".join(k_split)] = enzyme_dict.pop(key)
    ec_to_i = {e: i for i, e in enumerate(enzyme_dict.keys())}
    one_hot = {}
    for e, rs in enzyme_dict.items():
        for r in rs:
            one_hot.setdefault(r, np.zeros(len(ec_to_i), dtype=np.int32))[ec_to_i[e]] = 1
    reactants, enzymes = zip(*one_hot.items())
    reactants, enzymes = np.array(reactants), np.array(enzymes)
    val_splitter = MultilabelStratifiedShuffleSplit(n_splits=1, test_size=0.1, random_state=args.seed)
    train_ids, val_ids = list(val_splitter.split(reactants, enzymes))[0]
    x_train, y_train = reactants[train_ids], enzymes[train_ids]
    x_val, y_val = reactants[val_ids], enzymes[val_ids]
    x_train, y_train, x_val, y_val = x_train.tolist(), y_train.tolist(), x_val.tolist(), y_val.tolist()
    if final_train:
        x_train = x_train + x_val
        y_train = y_train + y_val
        x_val = []
        y_val = []
    fold_splits = {"train": x_train, "val": x_val, "e_train": y_train, "e_val": y_val, "ec_to_i": ec_to_i}
    return fold_splits


def download_envipath():
    os.makedirs("data/envipath", exist_ok=True)
    print("Downloading enviPath data")
    eP = enviPath('https://envipath.org')
    bbd = eP.get_package('https://envipath.org/package/32de3cf4-e3e6-4168-956e-32fa5ddb0ce1')
    soil = eP.get_package('https://envipath.org/package/5882df9c-dae1-4d80-a40e-db4724271456')
    sludge = eP.get_package('https://envipath.org/package/521c547a-fd2a-491c-ad5b-7eaa1577fb65')
    packages = [("bbd", bbd), ("soil", soil), ("sludge", sludge)]
    for name, package in packages:
        if not os.path.exists(save_path := f"data/envipath/{name}.json"):
            compounds = [c.get_json() for c in tqdm(package.get_compounds(), desc=f"Getting compounds for {name}")]
            reactions = [r.get_json() for r in tqdm(package.get_reactions(), desc=f"Getting reactions for {name}")]
            pathways = [p.get_json() for p in tqdm(package.get_pathways(), desc=f"Getting pathways for {name}")]
            with open(save_path, "w") as j_file:
                json.dump({"compounds": compounds, "reactions": reactions, "pathways": pathways}, j_file)


def process_compare_reactions(test_reactions, predictions, thresholds, top_k=-1):
    predictions, probabilities = predictions
    true_dict = {}
    for r in test_reactions:
        reactant, true_product_set = r.split(">>")
        true_product_set = {p for p in true_product_set.split(".")}
        true_dict[reactant] = true_dict.setdefault(reactant, []) + [true_product_set]
    pred_dict = {}
    assert len(test_reactions) == len(predictions)
    assert sum(len(v) for v in true_dict.values()) == len(test_reactions)
    for k, (pred_smiles, pred_proba) in enumerate(zip(predictions, probabilities)):
        reactant, true_product = test_reactions[k].split(">>")
        pred_dict.setdefault(reactant, {"predict": [], "scores": []})
        for smiles, proba in zip(pred_smiles, pred_proba):
            smiles = set(smiles.split("."))
            if smiles not in pred_dict[reactant]["predict"]:
                pred_dict[reactant]["predict"].append(smiles)
                pred_dict[reactant]["scores"].append(proba)

    correct = {t: 0 for t in thresholds}
    predicted = {t: 0 for t in thresholds}
    accuracy = {k + 1: [] for k in range(max([len(p) for p in predictions] + [top_k]))}
    for reactant, product_sets in true_dict.items():
        pred_smiles = pred_dict[reactant]["predict"]
        pred_scores = pred_dict[reactant]["scores"]

        for true_set in product_sets:
            top_k = max(accuracy.keys()) + 1
            for k, pred_set in enumerate(pred_smiles):
                if len(true_set - pred_set) == 0:
                    top_k = k + 1
                    break
            for k in accuracy:
                accuracy[k].append(k >= top_k)

            for threshold in correct:
                pred_s = [s for i, s in enumerate(pred_smiles) if pred_scores[i] > threshold]
                predicted[threshold] += len(pred_s)
                for pred_set in pred_s:
                    if len(true_set - pred_set) == 0:
                        correct[threshold] += 1
                        break

    recall = {k: v / len(test_reactions) for k, v in correct.items()}
    precision = {k: v / predicted[k] if predicted[k] > 0 else 0 for k, v in correct.items()}
    accuracy = {f"top_{k}": sum(v) / len(v) if len(v) > 0 else 0 for k, v in accuracy.items()}
    save_predictions = {}
    for reactant, true_products in true_dict.items():
        pred_smiles = pred_dict[reactant]["predict"]
        pred_smiles = [".".join(p) for p in pred_smiles]
        pred_scores = pred_dict[reactant]["scores"]
        true_products = [".".join(t) for t in true_products]
        save_predictions[reactant] = {"actual": true_products, "predict": pred_smiles, "scores": pred_scores}
    single_test_output = {"predictions": save_predictions, "recall": recall, "precision": precision, "accuracy": accuracy}
    return single_test_output


def get_thresholds(value_type=list):
    thresholds = {}
    thresholds.update({i / 50: value_type() for i in range(-750, -100, 25)})
    thresholds.update({i / 500: value_type() for i in range(-1000, -100, 25)})
    return thresholds


def get_moe_version(args, config):
    full_version = [args.data_name, str(config["ec_min"]),  str(config["ec_lvl"]), str(args.seed)]
    if args.weights_dataset:
        full_version.append(args.weights_dataset.split("/")[-1])
    if not config["use_enzyme"]:
        full_version.append("false")
    full_version = "_".join(full_version)
    return full_version


def get_all_moe_loaders(split, ec_to_i, tokenizer, config, args):
    x_train, y_train, x_val, y_val, x_test, y_test = split["train"], split["e_train"], split["val"], split["e_val"], split["test"], split["e_test"]
    eclipse_train, experts_train = make_moe_loader(x_train, y_train, tokenizer, ec_to_i, "train", config, args)
    eclipse_val, experts_val = make_moe_loader(x_val, y_val, tokenizer, ec_to_i, "val", config, args)
    eclipse_test, experts_test = make_moe_loader(x_test, y_test, tokenizer, ec_to_i, "test", config, args)
    if args.test:
        x_test = x_train + x_val + x_test
        y_test = y_train + y_val + y_test
    return eclipse_train, eclipse_val, eclipse_test, experts_train, experts_val, experts_test, x_test, y_test, x_val, y_val, ec_to_i


def make_moe_loader(reactions, enzymes, tokenizer, ec_to_i, set_type, config, args):
    eclipse_x = []
    eclipse_y = []
    expert_x = {}
    expert_y = {}
    batch_size = args.batch_size if set_type != "test" else args.batch_size // 2
    for reaction, enzyme in tqdm(zip(reactions, enzymes), total=len(reactions)):
        reactant, product = reaction.split(">>")
        reactant_e = encode_mol(reactant, tokenizer, args, enclose=False)
        product_e = encode_mol(product, tokenizer, args)
        if reactant_e is not None and product_e is not None:
            eclipse_y.append(ec_to_i[enzyme])
            eclipse_x.append(reactant_e)
        reactant_e = encode_mol(f"{reactant}>{enzyme}", tokenizer, args, enclose=False)
        if reactant_e is not None and product_e is not None:
            if not config.get("use_enzyme", True):
                reactant_e = encode_mol(reactant, tokenizer, args, enclose=False)
            e_id = -1
            expert_x.setdefault(e_id, []).append(reactant_e)
            expert_y.setdefault(e_id, []).append(product_e)
    eclipse_x = pad_sequence(eclipse_x, padding_value=tokenizer["[nop]"], batch_first=True)
    eclipse_y = torch.tensor(eclipse_y)
    eclipse_loader = DataLoader(TensorDataset(eclipse_x, eclipse_y), batch_size=batch_size,
                                 shuffle=set_type == "train", num_workers=args.workers, persistent_workers=True)
    expert_loaders = {}
    for expert_i in expert_x:
        x = pad_sequence(expert_x[expert_i], padding_value=tokenizer["[nop]"], batch_first=True)
        y = pad_sequence(expert_y[expert_i], padding_value=tokenizer["[nop]"], batch_first=True)
        loader = DataLoader(TensorDataset(x, y), batch_size=batch_size,
                            shuffle=set_type == "train", num_workers=args.workers, persistent_workers=True)
        expert_loaders[expert_i] = loader
    return eclipse_loader, expert_loaders


def encode_mol(mol: str, tokenizer: dict, args, enclose: bool = True):
    """
    :param mol: A string representing the molecule to be encoded.
    :param tokenizer: A dictionary containing the mapping of tokens to indices.
    :param args: Arguments related to the tokenizer.
    :param enclose: A boolean indicating whether to enclose the encoded sequence with special tokens.

    :return: A Tensor containing the encoded sequence, or None if encoding fails.
    """
    try:
        tokens = [tokenizer[token] for token in regex_tokenizer(mol)]
    except KeyError as e:
        return None
    if enclose:
        tokens = [tokenizer["som"]] + tokens + [tokenizer["eom"]]
    if len(tokens) > args.max_len or len(tokens) < args.min_len:
        return None
    return torch.tensor(tokens, dtype=torch.long)


def regex_tokenizer(smile: str) -> list:
    """Tokenizes a SMILES string using a regular expression.

    :param smile: The input SMILES string.
    :return: A list of tokens extracted from the SMILES string.
    """
    # pattern = r"(\[|\]|[A-Z][a-z]?|[A-Z]|[a-z]|:[0-9]{3}|:[0-9]{2}|:[0-9]|[0-9]|\(|\)|\.|=|#|-|\+|\\|\/|:|~|@@|@|\?|>>|>|\*|\$|\%)"
    pattern = r"(\[|\]|[A-Z][a-z]?|[A-Z]|[a-z]|:[0-9]{3}|:[0-9]{2}|:[0-9]|[0-9]|\(|\)|\.|=|#|-|\+|\\|\/|:|~|@@|@|\?|>>|>|\*|\$|\%)"

    regex = re.compile(pattern)
    tokens = regex.findall(smile)
    assert smile.strip() == ''.join(tokens), f"Regex SMILE is not the same as original SMILE\nOriginal:{smile}\nRegex:   {''.join(tokens)}"
    return tokens


def eclipse_split_to_moe(data_frame, eclipse_split, config, ec_to_i):
    ec_lvl = config["ec_lvl"]
    eclipse_split = eclipse_split.copy()
    r_train, r_val, r_test = set(eclipse_split["train"]), set(eclipse_split["val"]), set(eclipse_split["test"])
    unique_rs = set()
    train, e_train, val, e_val, test, e_test = [], [], [], [], [], []
    for row in data_frame.itertuples():
        reactant = row.rdkit_reactants
        reaction = row.rdkit_reaction
        ec_num = ".".join(row.ec_num.split(".")[:ec_lvl])
        pos = ec_lvl
        while ec_num not in ec_to_i and pos > 0:
            ec_num = ec_num.split(".")
            ec_num[pos := pos-1] = "-"
            ec_num = ".".join(ec_num)
        r_e_id = f"{reactant}>{ec_num}"
        if pos <= 0:
            continue
        elif reactant in r_train and r_e_id not in unique_rs:
            train.append(reaction)
            e_train.append(ec_num)
        elif reactant in r_val and r_e_id not in unique_rs:
            val.append(reaction)
            e_val.append(ec_num)
        elif reactant in r_test and r_e_id not in unique_rs:
            test.append(reaction)
            e_test.append(ec_num)
        unique_rs.add(r_e_id)
    eclipse_split["train"], eclipse_split["val"], eclipse_split["test"] = train, val, test
    eclipse_split["e_train"], eclipse_split["e_val"], eclipse_split["e_test"] = e_train, e_val, e_test
    return eclipse_split


def process_seq_test_outputs(outputs: list, path: str, i_to_char: dict, args) -> dict:
    RDLogger.DisableLog('rdApp.*')
    flat_outputs = [[], []]
    flat_scores = []
    flat_inputs = []
    for inputs, (predict, actual, score) in outputs:
        flat_scores.extend(score)
        flat_inputs.extend(inputs)
        flat_outputs[0].extend(predict)
        flat_outputs[1].extend(actual)
    results = Parallel(n_jobs=args.workers)(
        delayed(process_output)(inputs, predict, actual, score, i_to_char, args) for
        inputs, predict, actual, score in tqdm(zip(flat_inputs, flat_outputs[0], flat_outputs[1], flat_scores),
                                               total=len(flat_outputs[0]), desc="Decoding output"))
    results_dict = {}
    accuracy = {}
    invalid_smiles = {}
    if flat_outputs[0][0].ndim == 1:
        top_k = [1]
    else:
        top_k = range(1, len(flat_outputs[0][0]) + 1)
    for input_smiles, m_smiles, a_smiles, score in tqdm(results, desc="Calculating metrics"):
        if len(a_smiles) == 0 or len(input_smiles) == 0:
            continue
        if input_smiles not in results_dict:
            results_dict[input_smiles] = {"actual": [], "scores": [], "predict": {f"top_{k}": [] for k in top_k}}
        elif args.score_all:
            r_numbers = [1]
            for k in results_dict.keys():
                split = k.split(" ")
                if split[0] == input_smiles:
                    if len(split) > 1:
                        r_numbers.append(int(split[-1]) + 1)
            input_smiles += " " + str(max(r_numbers))
            results_dict[input_smiles] = {"actual": [], "scores": [], "predict": {f"top_{k}": [] for k in top_k}}
        # m_smiles = [set(m.split(".")) for m in m_smiles]
        results_dict[input_smiles]["actual"].append(a_smiles)
        results_dict[input_smiles]["scores"].append(score)
        for k in top_k:
            key = f"top_{k}"
            results_dict[input_smiles]["predict"][key].extend(m_smiles[:k])
    for reactant in results_dict:
        real_products = results_dict[reactant]["actual"]
        for k in top_k:
            key = f"top_{k}"
            pred_products = results_dict[reactant]["predict"][key]
            if key not in accuracy:
                accuracy[key] = []
            if key not in invalid_smiles:
                invalid_smiles[key] = []
            invalid_smiles[key].append(sum(int(len(p) == 0) for p in pred_products))
            for real in real_products:
                success = 0
                real = set(real.split("."))
                for predict in pred_products:
                    predict = set(predict.split("."))
                    if len(real - predict) == 0:  # This allows extra product to be predicted
                        # if real_inchi_set == pred_inchi_set:  # This requires no extras
                        success = 1
                        break
                accuracy[key].append(success)
    for key in accuracy:
        accuracy[key] = round(sum(accuracy[key]) / len(accuracy[key]), 4)
        invalid_smiles[key] = sum(invalid_smiles[key])
    recall, precision = precision_recall_threshold(results_dict, path, args)
    save_dict = {"invalid_smiles": invalid_smiles, "accuracy": accuracy,
                 "predictions": results_dict, "recall": recall, "precision": precision}

    with open(f"{path}/test_output.json", "w") as out_file:
        json.dump(save_dict, out_file, indent=4)
    return save_dict


def process_output(inputs, predict, actual, score, i_to_char, args):
    predict = predict.numpy()
    actual = actual.numpy()
    canon_func = canon_smile_rdkit
    inputs = inputs.numpy()
    input_smiles = decode_mol(inputs, i_to_char, canon_func)
    input_smiles = input_smiles.split(">")[0]
    score = score.numpy()
    if predict.ndim == 1:
        m_smiles = [decode_mol(predict, i_to_char, canon_func)]
    else:
        m_smiles = [decode_mol(beam, i_to_char, canon_func)
                    for beam in predict]
    a_smiles = decode_mol(actual, i_to_char, canon_func)
    return input_smiles, m_smiles, a_smiles, score.tolist()


def decode_mol(array, i_to_char, canon_func):
    decoded = [i_to_char[i] for i in array]
    smiles = "".join(decoded)
    smiles = remove_special_chars(smiles)
    mols = smiles.split(".")
    canon_mols = []
    for mol in mols:
        canon = canon_func(mol)
        if canon is not None and len(canon) > 0:
            canon_mols.append(canon)
    return ".".join(canon_mols)


def remove_special_chars(mol_str: str) -> str:
    special_chars = ["eom", "som", "[nop]"]
    for char in special_chars:
        mol_str = mol_str.replace(char, "")
    return mol_str


def canon_smile_rdkit(smile: str, allow_none=True, remove_stereochemistry=False) -> str | None:
    RDLogger.DisableLog('rdApp.*')
    mol = Chem.MolFromSmiles(smile)
    if allow_none and mol is None:
        return None
    elif mol is None:
        return smile
    if remove_stereochemistry:
        Chem.RemoveStereochemistry(mol)
    return Chem.MolToSmiles(mol, canonical=True)


def precision_recall_threshold(predictions, path, args, data_name=None, thresholds=None, save=True, extra_pr=None):
    if data_name is None:
        data_name = path.split("/")[-1]
    reactions = set()
    for input_smiles, prediction in predictions.items():
        input_smiles = input_smiles.split(" ")[0]
        actual_p = prediction["actual"]
        for a_p in actual_p:
            reactions.add(input_smiles + ">>" + a_p)
    if thresholds is None:
        thresholds = get_thresholds(value_type=set)
    max_score = float("-inf")
    min_score = 0.0
    results = Parallel(n_jobs=args.workers)(delayed(threshold_process)(t, predictions)
                                                       for t in tqdm(thresholds, desc="Calculating PR curve"))
    for threshold, pred_set, max_s, min_s in results:
        thresholds[threshold] = pred_set
        max_score = max(max_score, max_s)
        min_score = min(min_score, min_s)
    print(f"Minimum score: {min_score}")
    print(f"Maximum score: {max_score}")

    recall = {}
    precision = {}
    for threshold, pred_set in thresholds.items():
        num_correct = len(reactions) - len(reactions - pred_set)
        recall[threshold] = num_correct / len(reactions) if len(reactions) > 0 else 0.0
        precision[threshold] = num_correct / len(pred_set) if pred_set else 0.0

    # Sort the values by recall to ensure proper integration
    sorted_recall, sorted_precision, area_under_curve = sort_recall_precision(recall, precision)
    if save:
        plot_pr_curve(sorted_recall, sorted_precision, area_under_curve, data_name, path, extra_pr=extra_pr)
    return recall, precision


def threshold_process(threshold, predictions):
    pred_set = set()
    max_score = float("-inf")
    min_score = 0.0
    for input_smiles, prediction in predictions.items():
        input_smiles = input_smiles.split(" ")[0]
        scores = prediction["scores"][0]
        prediction = prediction["predict"]
        product_scores = {}
        top_k = list(prediction.keys())
        top_k = max(top_k, key=lambda x: int(x.split("_")[-1]))
        k_product = prediction[top_k]
        i = int(top_k.split("_")[-1])
        k_product = k_product[:i]
        for i, p in enumerate(k_product):
            if p in product_scores:
                product_scores[p].append(scores[i])
            else:
                product_scores[p] = [scores[i]]
        for product, score in product_scores.items():
            score = max(score)
            max_score = max(max_score, score)
            min_score = min(min_score, score)
            pred_reaction = input_smiles + ">>" + product
            if score >= threshold:
                pred_set.add(pred_reaction)
    return threshold, pred_set, max_score, min_score


def one_hots_to_hierarchies(one_hots, i_to_ec):
    hierarchies = []
    for one_hot in one_hots:
        ec_lvls = []
        for j in np.nonzero(one_hot)[0]:
            ec_split = i_to_ec[j.item()].split(".")
            ec_lvls.append([".".join(ec_split[:lvl]) for lvl in range(1, len(ec_split) + 1)])
        hierarchies.append(ec_lvls)
    return hierarchies


def canon_smirk(smirk, canon_func, allow_none=False):
    smirk = smirk.strip()
    reactant, product = smirk.split(">>")[:2]

    def canon_r_side(side):
        canon = []
        for r in side.split(">"):
            c_r = canon_func(r)
            if c_r:
                canon.append(c_r)
        canon = ">".join(canon)
        if len(canon) == 0:
            return None
        return canon

    canon_reactant = canon_r_side(reactant)
    canon_product = canon_r_side(product)
    if allow_none and (canon_reactant is None or canon_product is None):
        return None
    if canon_reactant is None:
        canon_reactant = reactant
    if canon_product is None:
        canon_product = product
    return canon_reactant + ">>" + canon_product


def save_train_metrics(model_metrics: dict[str, dict], path: str, steps_per_epoch: dict):
    metrics = copy.deepcopy(model_metrics)
    for metric in metrics:
        for s_type in metrics[metric]:
            means = [mean(metrics[metric][s_type][i:i + steps_per_epoch[s_type]]) for i in
                     range(0, len(metrics[metric][s_type]), steps_per_epoch[s_type])]
            metrics[metric][s_type] = means

    with open(f"{path}/train_metrics.json", "w") as m_file:
        json.dump(metrics, m_file, indent=4)
    plt.clf()
    fig, axs = plt.subplots(len(metrics), sharex="all")
    fig.set_size_inches(18, 5 * len(metrics))
    plt.suptitle(f"Train Metrics for {path}")
    SMALL_SIZE = 16
    MEDIUM_SIZE = 20
    BIGGER_SIZE = 26
    axs = axs.flat
    for i, (metric, values) in enumerate(metrics.items()):
        axs[i].set_title(metric, fontsize=BIGGER_SIZE)
        step_num = len(max(values.values(), key=lambda x: len(x)))
        for step_type, value in values.items():
            x_step = step_num // len(value) if len(value) > 0 else 1
            x_coords = list(range(0, step_num, x_step))
            axs[i].plot(x_coords[:len(value)], value, label=step_type)
        axs[i].tick_params(axis='both', which='major', labelsize=SMALL_SIZE)
        axs[i].tick_params(axis='both', which='minor', labelsize=SMALL_SIZE)
        axs[i].set_xlabel('Epoch', fontsize=SMALL_SIZE)
        axs[i].legend(list(values.keys()), loc="lower left", fontsize=MEDIUM_SIZE)
    plt.tight_layout()
    plt.savefig(f"{path}/train_metrics.png", dpi=120)
    plt.close()


def _sort_beams(mol_strs, log_lhs, all_ll):
    """ Return mols sorted by their log likelihood"""

    assert len(mol_strs) == len(log_lhs)

    sorted_mols = []
    sorted_lls = []
    sorted_all_ll = []

    for mols, lls, all_ls in zip(mol_strs, log_lhs, all_ll):
        mol_lls = sorted(zip(mols, lls, all_ls), reverse=True, key=lambda mol_ll: mol_ll[1])
        mols, lls, all_ls = tuple(zip(*mol_lls))
        sorted_mols.append(torch.stack(mols))
        sorted_lls.append(torch.stack(lls))
        sorted_all_ll.append(torch.stack(all_ls))

    return torch.stack(sorted_mols), torch.stack(sorted_lls), torch.stack(sorted_all_ll)


def beam_step(decode_func, model, tokens, lls):
    output_dist = decode_func(tokens)
    next_token_lls = output_dist[:, -1, :]
    _, vocab_size = next_token_lls.size()
    complete_seq_ll = torch.ones(1, vocab_size,
                                 device=output_dist.device) * -1e5  # Use -1e5 for log softmax or 0 for softmax
    complete_seq_ll[:, model.char_to_i["[nop]"]] = 0.0  # Use 0.0 for log softmax or 1.0 for softmax

    # Use this vector in the output for sequences which are complete
    is_end_token = tokens[:, -1] == model.char_to_i["eom"]
    is_pad_token = tokens[:, -1] == model.char_to_i["[nop]"]
    ll_mask = torch.logical_or(is_end_token, is_pad_token).unsqueeze(1)
    masked_lls = (ll_mask * complete_seq_ll) + (~ll_mask * next_token_lls)

    seq_lls = (lls + masked_lls.T).T
    return seq_lls


def norm_length(seq_lls, mask, length_norm=None):
    """ Normalise log-likelihoods using the length of the constructed sequence
    Equation from:
    Wu, Yonghui, et al.
    "Google's neural machine translation system: Bridging the gap between human and machine translation."
    arXiv preprint arXiv:1609.08144 (2016).

    Args:
        seq_lls (torch.Tensor): Tensor of shape [batch_size, vocab_size] containing log likelihoods for seqs so far
        mask (torch.Tensor): BoolTensor of shape [seq_len, batch_size] containing the padding mask
        length_norm (int): Length norm value

    Returns:
        norm_lls (torch.Tensor): Tensor of shape [batch_size, vocab_size]

    """

    if length_norm is not None:
        seq_lengths = (~mask).sum(dim=1)
        norm = torch.pow(5 + seq_lengths, length_norm) / pow(6, length_norm)
        norm_lls = (seq_lls.T / norm).T
        return norm_lls

    return seq_lls


def update_beams(i, decode_func, model, token_ids_list, pad_mask_list, lls_list, all_ll, length_norm):
    """Update beam tokens and pad mask in-place using a single decode step

    Updates token ids and pad mask in-place by producing the probability distribution over next tokens
    and choosing the top k (number of beams) log likelihoods to choose the next tokens.
    Sampling is complete if every batch element in every beam has produced an end token.
    """

    assert len(token_ids_list) == len(pad_mask_list) == len(lls_list)

    num_beams = len(token_ids_list)

    ts = [token_ids[:, :i] for token_ids in token_ids_list]
    ms = [pad_mask[:, :i] for pad_mask in pad_mask_list]

    # Apply current seqs to model to get a distribution over next tokens
    # new_lls is a tensor of shape [batch_size, vocab_size * num_beams]
    new_lls = [beam_step(decode_func, model, t, lls) for t, lls in zip(ts, lls_list)]
    norm_lls = [norm_length(lls, mask, length_norm) for lls, mask in zip(new_lls, ms)]

    _, vocab_size = tuple(new_lls[0].shape)
    new_lls = torch.cat(new_lls, dim=1)
    norm_lls = torch.cat(norm_lls, dim=1)

    # Keep lists (of length num_beams) of tensors of shape [batch_size]
    top_lls, top_idxs = torch.topk(norm_lls, num_beams, dim=1)
    all_ll[:, :, i] += top_lls
    new_ids_list = list((top_idxs % vocab_size).T)
    beam_idxs_list = list((top_idxs // vocab_size).T)
    top_lls = [new_lls[b_idx, idx] for b_idx, idx in enumerate(list(top_idxs))]
    top_lls = torch.stack(top_lls).T

    beam_complete = []
    new_ts_list = []
    new_pm_list = []
    new_lls_list = []

    # Set the sampled tokens, pad masks and log likelihoods for each of the new beams
    for new_beam_idx, (new_ids, beam_idxs, lls) in enumerate(zip(new_ids_list, beam_idxs_list, top_lls)):
        # Get the previous sequences corresponding to the new beams
        token_ids = [token_ids_list[beam_idx][b_idx, :] for b_idx, beam_idx in enumerate(beam_idxs)]
        token_ids = torch.stack(token_ids)

        # Generate next elements in the pad mask. An element is padded if:
        # 1. The previous token is an end token
        # 2. The previous token is a pad token
        is_end_token = token_ids[:, i - 1] == model.char_to_i["eom"]
        is_pad_token = token_ids[:, i - 1] == model.char_to_i["[nop]"]
        new_pad_mask = torch.logical_or(is_end_token, is_pad_token)
        beam_complete.append(new_pad_mask.sum().item() == new_pad_mask.numel())

        # Ensure all sequences contain an end token
        if i == model.max_len - 1:
            new_ids[~new_pad_mask] = model.char_to_i["eom"]

        # Set the tokens to pad if an end token as already been produced
        new_ids[new_pad_mask] = model.char_to_i["[nop]"]
        token_ids[:, i] = new_ids

        # Generate full pad mask sequence for new token sequence
        pad_mask = [pad_mask_list[beam_idx][b_idx, :] for b_idx, beam_idx in enumerate(beam_idxs)]
        pad_mask = torch.stack(pad_mask)
        pad_mask[:, i] = new_pad_mask

        # Add tokens, pad mask and lls to list to be updated after all beams have been processed
        new_ts_list.append(token_ids)
        new_pm_list.append(pad_mask)
        new_lls_list.append(lls)

    complete = sum(beam_complete) == len(beam_complete)

    # Update all tokens, pad masks and lls
    if not complete:
        for beam_idx, (ts, pm, lls) in enumerate(zip(new_ts_list, new_pm_list, new_lls_list)):
            token_ids_list[beam_idx] = ts
            pad_mask_list[beam_idx] = pm
            lls_list[beam_idx] = lls

    return complete


def beam_decode(model, x, num_beams: int = 8):
    if model.__class__.__name__ == "TransformerModel":
        z, src_mask = model.encode(x)
        decode_func = partial(model.decode, enc_out=z, src_mask=src_mask, test=True)
    elif model.__class__.__name__ == "StringAutoEncoder":
        z, src_mask = model.encode(x)
        decode_func = partial(model.decode, z=z, src_mask=src_mask, test=True)
    elif model.__class__.__name__ == "ModularModel":
        z, src_masks = model.encode(x)
        decode_func = partial(model.decode, enc_out=z, src_masks=src_masks, test=True)
    elif model.__class__.__name__ == "GNNModel":
        z, lengths = model.encode(x)
        decode_func = partial(model.decode, src_enc=z, lengths=lengths, test=True)
    else:
        raise ValueError(f"Model of type {model.__class__.__name__} cannot be beam decoded")
    token_ids = [([model.char_to_i["som"]] + ([model.char_to_i["[nop]"]] * (model.max_len - 1)))] * z.size(0)
    token_ids = torch.tensor(token_ids, device=z.device)
    pad_mask = torch.zeros(z.size(0), model.max_len, device=z.device, dtype=torch.bool)
    ts = token_ids[:, :1]
    all_ll = torch.zeros((z.size(0), num_beams, model.max_len), device=z.device)
    ll = torch.zeros(z.size(0), device=z.device)
    first_lls = beam_step(decode_func, model, ts, ll)
    top_lls, top_ids = torch.topk(first_lls, num_beams, dim=-1)
    all_ll[:, :, 1] += top_lls
    top_ids = list(top_ids.T)

    token_ids_list = [token_ids.clone() for _ in range(num_beams)]
    pad_mask_list = [pad_mask.clone() for _ in range(num_beams)]
    lls_list = list(top_lls.T)

    for beam_id, ids in enumerate(top_ids):
        token_ids_list[beam_id][:, 1] = ids
        pad_mask_list[beam_id][:, 1] = False

    for i in range(2, model.max_len):
        complete = update_beams(i, decode_func, model, token_ids_list, pad_mask_list, lls_list, all_ll,
                                model.model_config["length_norm"])
        if complete:
            break

    tokens_tensor = torch.stack(token_ids_list).permute(1, 0, 2)
    log_lhs_tensor = torch.stack(lls_list).permute(1, 0)
    sorted_mols, sorted_lls, sorted_all_lls = _sort_beams(tokens_tensor, log_lhs_tensor, all_ll)

    return sorted_mols, sorted_lls, sorted_all_lls


def encode_reactions(data: list, tokenizer: dict, args) -> TensorDataset:
    x = []
    y = []
    scenario_data = []
    failed_encoding = 0
    max_len = 0
    scenario_dict = {}
    enzyme_dict = {}
    if args.enzymes:
        enzyme_dict = create_enzyme_info(args)

    parallel_out = Parallel(n_jobs=args.workers, batch_size=500)(
        delayed(inner)(reaction, tokenizer, args, scenario_dict, enzyme_dict) for reaction in tqdm(data))
    for p_out in parallel_out:
        enc_reactants, enc_products, s_data = p_out
        for enc_r, enc_p in zip(enc_reactants, enc_products):
            if enc_r is None or enc_p is None:
                failed_encoding += p_out.count(None)
                continue
            max_len = max(len(enc_r), len(enc_p), max_len)
            x.append(enc_r)
            y.append(enc_p)
            scenario_data.append(s_data)
    print(f"Failed to encode {failed_encoding} SMILES")
    print(f"Longest SMILES is {max_len} tokens.")
    x = pad_sequence(x, padding_value=tokenizer["[nop]"], batch_first=True)
    y = pad_sequence(y, padding_value=tokenizer["[nop]"], batch_first=True)
    if args.scenario:
        scenario_data = torch.stack(scenario_data)
        data = TensorDataset(x, scenario_data, y)
    else:
        data = TensorDataset(x, y)
    return data


def inner(reaction: str, tokenizer: dict, args, enzyme_dict) -> tuple:
    reactant, product = reaction.split(">>")[:2]
    enc_p = encode_mol(product, tokenizer, args)
    if args.enzymes:
        enzyme_data = enzyme_dict.get(reaction, [""])
        r_with_e = []
        for enzyme in enzyme_data:
            r_with_e.append(encode_mol(reactant + f">{enzyme}", tokenizer, args, enclose=False))
        enc_p = [enc_p] * len(r_with_e)
        return r_with_e, enc_p
    enc_r = encode_mol(reactant, tokenizer, args, enclose=False)
    return [enc_r], [enc_p]


def create_enzyme_info(args, ec_lvl=3):
    packages = ["soil", "bbd", "sludge"]
    path = f"data/{args.data_name}_{args.preprocessor}_enzyme_info.json"
    if os.path.exists(path):
        with open(path) as file:
            r_to_e = json.load(file)
        return r_to_e
    r_to_e = {}
    canon_func = canon_smile_rdkit
    if "ecmap" in args.data_name:
        data = pd.read_csv("data/ecmap/all_reactions.csv")
        data = data.drop_duplicates(["rdkit_reaction", "ec_num"])
        for row in tqdm(data.itertuples(), total=data.shape[0]):
            reaction = row.rdkit_reaction
            enzyme = ".".join(row.ec_num.split(".")[:ec_lvl]) if pd.notna(row.ec_num) else None
            if enzyme is not None:
                r_to_e[reaction] = r_to_e.setdefault(reaction, set()) | {enzyme}
        r_to_e = {r: list(e) for r, e in r_to_e.items()}
    else:
        for package in packages:
            with open(f"data/envipath/{package}.json") as d_file:
                data = json.load(d_file)
            for reaction in data["reactions"]:
                if "ecNumbers" in reaction:
                    if len(reaction["ecNumbers"]) == 1:
                        enzyme = reaction["ecNumbers"][0]["ecNumber"]
                        enzyme = ".".join(enzyme.split(".")[:ec_lvl])
                        r_smirks = canon_smirk(reaction["smirks"], canon_func)
                        r_to_e[r_smirks] = enzyme
                        for pathway in reaction["pathways"]:
                            r_to_e[pathway["name"]] = r_to_e.setdefault(pathway["name"], []) + [enzyme]
                    elif len(reaction["ecNumbers"]) > 1:
                        raise ValueError("More than one enzyme for reaction")

    with open(path, "w") as e_file:
        json.dump(r_to_e, e_file)
    return r_to_e


def get_loaders(train: TensorDataset, val: TensorDataset, test: TensorDataset, batch_size: int | tuple, args):
    """
    Generate data loaders for training, validation, and test sets.

    :param train: The training dataset as a TensorDataset.
    :param val: The validation dataset as a TensorDataset.
    :param test: The test dataset as a TensorDataset.
    :param batch_size: The batch size for the data loaders.
    :param args: Additional arguments.
    :return: A tuple containing the training, validation, and test data loaders.
    """
    num_workers = args.workers
    if type(batch_size) is tuple:
        train_size, val_size, test_size = batch_size
    else:
        train_size, val_size, test_size = batch_size, batch_size, batch_size
    train_loader = DataLoader(train, batch_size=train_size, shuffle=True, num_workers=num_workers, persistent_workers=True)
    val_loader = DataLoader(val, batch_size=val_size, shuffle=False, num_workers=num_workers, persistent_workers=True)
    test_loader = DataLoader(test, batch_size=test_size, shuffle=False, num_workers=num_workers,
                             persistent_workers=True)
    return train_loader, val_loader, test_loader


def get_data_splits(data: list, train_ratio: float = None, seed=1) -> tuple[list, list, list]:
    reactants = []
    reactant_set = set()
    for r in data:
        reactant = r.split(">>")[0]
        if reactant not in reactant_set:
            reactants.append(reactant)
            reactant_set.add(reactant)
    mapping = False
    if any(":" in r for r in reactants):
        mapping = True
        reactants = [remove_mapping(r) for r in reactants]
    train, val, test = split_data(reactants, train_ratio, seed)
    train = set(train)
    val = set(val)
    test = set(test)
    if mapping:
        train = [r for r in data if remove_mapping(r.split(">>")[0]) in train]
        val = [r for r in data if remove_mapping(r.split(">>")[0]) in val]
        test = [r for r in data if remove_mapping(r.split(">>")[0]) in test]
    else:
        train = [r for r in data if r.split(">>")[0] in train]
        val = [r for r in data if r.split(">>")[0] in val]
        test = [r for r in data if r.split(">>")[0] in test]
    return train, val, test


def remove_mapping(smiles, canonical=True):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return smiles
    for atom in mol.GetAtoms():
        atom.SetAtomMapNum(0)
    return Chem.MolToSmiles(mol, canonical=canonical)


def split_data(data: list, split: float = None, seed=1):
    if split is None:
        split = 0.9
        if len(data) >= 25000:
            split = 0.95
        elif len(data) >= 100000:
            split = 0.98
    train_val_data, test_data = train_test_split(data, train_size=split, shuffle=True, random_state=seed)
    train_data, val_data = train_test_split(train_val_data, test_size=len(test_data), shuffle=True, random_state=seed)
    return train_data, val_data, test_data


def convert_eclipse_type(eclipse_type):
    if eclipse_type.lower() in {'h', 'hierarchy', 'h-eclipse'}:
        return "hierarchy"
    elif eclipse_type.lower() in {'f', 'flat', 'f-eclipse'}:
        return "flat"
    else:
        raise ValueError(f"Unknown eclipse type {eclipse_type.lower()}. Valid types are h (hierarchy) or f (flat)")


def prepare_envipath_data():
    download_envipath()
    table = {"dataset", "reactant", "product", "rdkit_reaction", "rdkit_reactants", "rdkit_products", "envipath_reaction", "pathway", "ec_num", "depth"}
    table = {k: [] for k in table}
    packages = ["soil", "bbd", "sludge"]
    for package in packages:
        with open(f"data/envipath/{package}.json") as d_file:
            data = json.load(d_file)
        pathways = {p["name"]: p for p in data["pathways"]}
        reactions: list[dict] = data["reactions"]
        for reaction in tqdm(reactions, desc=package):
            reactant, product = reaction["smirks"].split(">>")
            enzymes = [e["ecNumber"] for e in reaction.get("ecNumbers", [])]
            enzymes = " ".join(enzymes)
            rdkit = canon_smirk(reaction["smirks"], canon_smile_rdkit)
            if rdkit:
                r_rdkit, p_rdkit = rdkit.split(">>")
            else:
                r_rdkit, p_rdkit = "", ""
            if reaction.get("pathways", False):
                r_name = reaction["name"]
                for pathway in reaction["pathways"]:
                    pathway = pathways[pathway["name"]]
                    r_link = [l for l in pathway["links"] if l["name"] == r_name][0]
                    r_depth = pathway["nodes"][r_link["source"]]["depth"]
                    table["dataset"].append(package)
                    table["reactant"].append(reactant)
                    table["product"].append(product)
                    table["rdkit_reaction"].append(f"{r_rdkit}>>{p_rdkit}")
                    table["rdkit_reactants"].append(r_rdkit)
                    table["rdkit_products"].append(p_rdkit)
                    table["envipath_reaction"].append(f"{reactant}>>{product}")
                    table["pathway"].append(pathway["name"])
                    table["ec_num"].append(enzymes)
                    table["depth"].append(r_depth)
                    for key in table:
                        if len(table[key]) < len(table["dataset"]):
                            table[key].append("")
            else:
                table["dataset"].append(package)
                table["reactant"].append(reactant)
                table["product"].append(product)
                table["rdkit_reaction"].append(f"{r_rdkit}>>{p_rdkit}")
                table["rdkit_reactants"].append(r_rdkit)
                table["rdkit_products"].append(p_rdkit)
                table["envipath_reaction"].append(f"{reactant}>>{product}")
                table["pathway"].append("")
                table["ec_num"].append(enzymes)
                table["depth"].append(-2)
                for key in table:
                    if len(table[key]) < len(table["dataset"]):
                        table[key].append("")
    table = pd.DataFrame.from_dict(table)
    table.to_csv("data/envipath.csv", index=False)


if __name__ == "__main__":
    prepare_envipath_data()
    pass
