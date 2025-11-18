import json
import os.path
from importlib import resources
from chem_eclipse.ModelAnalysis import eclipse_per_seed
from chem_eclipse.models.ECLIPSEModel import ECLIPSEModel
from chem_eclipse.utils import convert_eclipse_type
from chem_eclipse.utils import get_arguments, get_dataset_eclipse, split_eclipse, expand_search_space


def train_one(args):
    with resources.files("chem_eclipse.models").joinpath("ECLIPSEModel_config.json").open("r") as c_file:
        config = json.load(c_file)
    train(args, config)


def train(args, config):
    config.update(vars(args))
    data = get_dataset_eclipse(args)
    fold_splits = split_eclipse(data, config, args)
    ec_to_i = fold_splits["ec_to_i"]
    model = ECLIPSEModel(ec_to_i, config, args, device="cuda" if args.gpu else 'cpu')
    with open(os.path.join(model.save_path, "split.json"), "w") as s_file:
        json.dump(fold_splits, s_file)
    print(f"Training eclipse version: {model.get_version()}")
    x_train, y_train, x_val, y_val, x_test, y_test = (fold_splits["train"], fold_splits["e_train"],
                                                      fold_splits["val"], fold_splits["e_val"],
                                                      fold_splits["test"], fold_splits["e_test"])
    if args.debug:
        x_train, y_train = x_train[:10000:10], y_train[:10000:10]
        x_val, y_val = x_val[:10000:10], y_val[:10000:10]
        x_test, y_test = x_test[:10000:10], y_test[:10000:10]

    if not os.path.exists(os.path.join(model.save_path, "model.pkl")):
        model.train(x_train, y_train, x_val, y_val)
    else:
        model = model.load_model()
        model.test(x_val, y_val, test_type="val", force_rerun=True)
    model.test(x_test, y_test, force_rerun=True)


def train_many(args, **kwargs):
    with resources.files("chem_eclipse.models").joinpath("ECLIPSEModel_config.json").open("r") as c_file:
        config = json.load(c_file)
    eclipse_type = convert_eclipse_type(args.eclipse_type)
    if "search_space" in kwargs:
        search_space = kwargs["search_space"]
    elif eclipse_type == "hierarchy":
        search_space = {"n_estimators": [20, 50, 100, 200, 500], "max_depth": [3, 6, 9, 12, 15],
                        "seed": list(range(10))}
    elif eclipse_type == "flat":
        search_space = {"n_estimators": [20, 50, 100, 200, 500], "max_depth": [3, 6, 9, 12, 15],
                        "seed": list(range(10)), "n_chains": [5, 10, 20, 40]}
    search_space = expand_search_space(search_space)
    for search in search_space:
        for k, v in search.items():
            if k in vars(args):
                setattr(args, k, v)
            elif k not in config:
                raise ValueError(f"Search space key {k} not in args")
        for k, v in config.items():
            if k not in search:
                search[k] = v
        train(args, search)
    eclipse_per_seed(eclipse_type)


def eclipse_train_main(**kwargs):
    arguments = get_arguments()
    if arguments.train_many:
        train_many(arguments, **kwargs)
    else:
        train_one(arguments)


if __name__ == "__main__":
    eclipse_train_main()
