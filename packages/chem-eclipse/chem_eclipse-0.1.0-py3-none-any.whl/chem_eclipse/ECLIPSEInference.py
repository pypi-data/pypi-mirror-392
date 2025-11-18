import json
import os.path
from importlib import resources
from chem_eclipse.ModelAnalysis import inference_distribution
from chem_eclipse.models.ECLIPSEModel import ECLIPSEModel
from chem_eclipse.utils import get_arguments, get_dataset_eclipse, expand_search_space, split_eclipse_inference


def train(args, config, final_train=False, **kwargs):
    config.update(vars(args))
    data = get_dataset_eclipse(args)
    split = split_eclipse_inference(data, config, args, final_train)
    x_train, y_train, x_val, y_val, ec_to_i = split["train"], split["e_train"], split["val"], split["e_val"], split["ec_to_i"]
    model = ECLIPSEModel(ec_to_i, config, args, device="cuda" if args.gpu else 'cpu', save_path=kwargs.get("save_path", None), no_folder=True)
    model.save_path = f"results/summary/{args.data_name}_final/{model.get_version()}" + ("_final" if final_train else "") \
        if not kwargs.get("save_path", False) else kwargs.get("save_path", False)
    os.makedirs(model.save_path, exist_ok=True)

    print(f"Training eclipse version: {model.get_version()}")
    if args.debug:
        x_train, y_train = x_train[:10000:10], y_train[:10000:10]
        x_val, y_val = x_val[:10000:10], y_val[:10000:10]

    if not os.path.exists(os.path.join(model.save_path, "model.pkl")):
        with open(os.path.join(model.save_path, "split.json"), "w") as s_file:
            json.dump(split, s_file)
        model.train(x_train, y_train, x_val, y_val)
    else:
        if final_train or (x_val and y_val):
            model = model.load_model()
        if x_val and y_val and not os.path.exists(os.path.join(model.save_path, f"val_tol_output.json")):
            model.test(x_val, y_val, test_type="val")
    return model, model.save_path


def train_many(args, **kwargs):
    with resources.files("chem_eclipse.models").joinpath("ECLIPSEModel_config.json").open("r") as c_file:
        config = json.load(c_file)
    if "search_space" in kwargs:
        search_space = kwargs.get("search_space")
    else:
        search_space = {"n_estimators": [20, 50, 100, 200, 500], "max_depth": [3, 6, 9, 12, 15]}
    search_space = expand_search_space(search_space)
    if args.debug:
        search_space = search_space[:2]
    results = []
    for search in search_space:
        for k, v in search.items():
            if k in vars(args):
                setattr(args, k, v)
            elif k not in config:
                raise ValueError(f"Search space key {k} not in args")
        for k, v in config.items():
            if k not in search:
                search[k] = v
        _, save_path = train(args, search)
        with open(os.path.join(save_path, f"val_tol_output.json")) as r_file:
            val_results = json.load(r_file)
        top_tol = max(val_results, key=lambda x: val_results[x]['f1'])
        val_results = val_results[top_tol]
        results.append((search, top_tol, val_results["f1"], save_path))
    best_config, top_tol, top_val, best_path = max(results, key=lambda x: x[-1])
    print(f"Top Val: {top_val:.4f} at {best_path}")
    best_model, best_path = train(args, best_config, final_train=True)
    best_model.tolerance = float(top_tol)
    if not args.test:
        raise ValueError("Inference requires defining an inference set")
    inference_data = get_dataset_eclipse(args, test=True)
    inference(best_model, inference_data, args)


def inference(model, data_frame, args):
    reactants = data_frame["rdkit_reactants"].to_list()
    predictions = model.predict(reactants)
    results = [list(comb) for comb in zip(reactants, predictions)]
    with open(f"results/summary/{args.data_name}_final/{args.test}_pred.json", "w") as p_file:
        json.dump(results, p_file)
    inference_distribution(args.data_name, args.test)


def eclipse_inference_main():
    arguments = get_arguments()
    train_many(arguments)


def oob_inference():
    arguments = get_arguments()
    if arguments.test == "":
        raise ValueError("ecmap_heclipse_inference needs the argument --test to be set, try bbd or your own csv path")
    data = get_dataset_eclipse(arguments, True)
    print(f"Performing inference with existing H-eclipse model on {arguments.data_name}")
    with resources.files(f"chem_eclipse.models.{arguments.data_name}_heclipse").joinpath("ec_to_i.json").open("r") as e_file:
        ec_to_i = json.load(e_file)["ec_to_i"]
    with resources.files(f"chem_eclipse.models.{arguments.data_name}_heclipse").joinpath("config.json").open("r") as c_file:
        config = json.load(c_file)
    model_path = resources.files("chem_eclipse.models").joinpath(f"{arguments.data_name}_heclipse")
    if os.path.exists(os.path.join(model_path, "model.pkl")):
        model = ECLIPSEModel(ec_to_i, config, arguments, device="cuda" if arguments.gpu else 'cpu', save_path=model_path)
        model = model.load_model(model_path)
    else:
        model, _ = train(arguments, config, True, save_path=model_path)
    model.tolerance = config["tolerance"]
    predictions = model.predict(data["rdkit_reactants"].to_list())
    os.makedirs("results/summary", exist_ok=True)
    with open(f"results/summary/{arguments.test}_pred.json", "w") as p_file:
        json.dump(predictions, p_file)


if __name__ == "__main__":
    oob_inference()
