from importlib import resources
from chem_eclipse.utils import *
from argparse import Namespace
import lightning as L
from lightning.pytorch.loggers import TensorBoardLogger
from lightning.pytorch.callbacks import LearningRateMonitor, ModelCheckpoint, EarlyStopping
import math
from chem_eclipse.models.ECLIPSEProdModel import ECLIPSEProdModel


def build_trainer(args, config: dict, monitor_value="val_seq_acc", version="") -> L.Trainer:
    full_version = get_moe_version(args, config) + "/" + version
    logger = TensorBoardLogger(f"results/", name="ECLIPSEProdModel", version=full_version)
    lr_monitor = LearningRateMonitor(logging_interval="epoch")
    patience = 5
    monitor_mode = "max" if "acc" in monitor_value else "min"
    early_stopping = EarlyStopping(monitor=monitor_value, mode=monitor_mode, patience=patience,
                                   check_on_train_epoch_end=False)
    checkpoint_cb = ModelCheckpoint(monitor=monitor_value, mode=monitor_mode)
    callbacks = [lr_monitor, checkpoint_cb, early_stopping]
    return L.Trainer(accelerator="auto", logger=logger, strategy="auto", callbacks=callbacks,
                     default_root_dir=f"results/ECLIPSEProdModel/{full_version}",
                     max_epochs=127 if args.debug else args.epochs, gradient_clip_val=1.0,
                     accumulate_grad_batches=1, log_every_n_steps=10,
                     num_sanity_val_steps=0, deterministic="warn", limit_train_batches=2 if args.debug else 1.0,
                     limit_test_batches=2 if args.debug else 1.0, limit_val_batches=2 if args.debug else 1.0)


def setup_model(args: Namespace):
    with resources.files("chem_eclipse.models").joinpath("ECLIPSEProdModel_config.json").open("r") as config_file:
        config = json.load(config_file)
    args_dict = {k: v for k, v in vars(args).items() if v is not None}
    config.update(args_dict)
    model_class = ECLIPSEProdModel
    print(config)
    return model_class, config


def train_one(args):
    model_class, config = setup_model(args)
    train(args, model_class, config)


def train_test_expert(expert_model, experts_train, experts_val, experts_test, ec_num, ckpt_path, version, args):
    expert_path = os.path.join(expert_model.save_path, "checkpoints")
    loaded = False
    if os.path.exists(expert_path) and os.listdir(expert_path):
        expert_checkpoint = os.path.join(expert_path, os.listdir(expert_path)[0])
        expert_model.load_state_dict(torch.load(expert_checkpoint)["state_dict"])
        loaded = True
    if not args.test:
        train_loader, val_loader, test_loader = experts_train[ec_num], experts_val[ec_num], experts_test[ec_num]
        expert_model.train_steps = math.ceil(len(train_loader) * args.epochs)
        trainer = build_trainer(args, expert_model.model_config, version=version)
        if not loaded:
            trainer.fit(expert_model, train_loader, val_loader, ckpt_path=ckpt_path)
            expert_model.load_state_dict(torch.load(trainer.checkpoint_callback.best_model_path)["state_dict"])
        trainer.test(expert_model, test_loader)
        expert_model.test_type = "val"
        trainer.test(expert_model, val_loader)
        expert_model.test_type = "test"


def train(args, model_class, config):
    print(
        f"Debug: {args.debug}\nModel: ECLIPSEProdModel\nDataset: {args.data_name}")
    print("Setting up")
    L.seed_everything(args.seed, workers=True)
    torch.set_float32_matmul_precision('high')
    os.makedirs(f"results/ECLIPSEProdModel/{get_moe_version(args, config)}", exist_ok=True)
    print(f"Version: {get_moe_version(args, config)}")
    data = get_dataset_eclipse(args)
    with resources.files("chem_eclipse.models").joinpath("tokenizers_stereo.json").open("r") as token_file:
        tokenizers = json.load(token_file)
    char_to_i = tokenizers['regex']
    i_to_char = {i: char for char, i in char_to_i.items()}
    tokenizer = (char_to_i, i_to_char)
    eclipse_fold_splits = split_eclipse(data, config, args)
    ec_to_i = eclipse_fold_splits["ec_to_i"]
    moe_fold_splits = eclipse_split_to_moe(data, eclipse_fold_splits, config, ec_to_i)
    result_path = f"results/ECLIPSEProdModel/{get_moe_version(args, config)}"
    with open(os.path.join(result_path, f"split_{args.data_name}.json"), "w") as s_file:
        json.dump(moe_fold_splits, s_file)
    (eclipse_train, eclipse_val, eclipse_test, experts_train, experts_val, experts_test, x_test_raw, y_test_raw, x_val_raw,
     y_val_raw, ec_to_i) = get_all_moe_loaders(moe_fold_splits, ec_to_i, tokenizer[0], config, args)
    train_steps = math.ceil(len(eclipse_train) * args.epochs)

    if args.weights_dataset:
        ckpt_path = f"{args.weights_dataset}/checkpoints/"
        ckpt_path = os.path.join(ckpt_path, [f for f in os.listdir(ckpt_path) if ".ckpt" in f][0])
    else:
        ckpt_path = None
    model = model_class(config, vocab=tokenizer, ec_vocab=ec_to_i, p_args=args, train_steps=train_steps)

    # Train the eclipse model
    x_train, y_train, x_val, y_val, x_test, y_test = (eclipse_fold_splits["train"], eclipse_fold_splits["e_train"],
                                                      eclipse_fold_splits["val"], eclipse_fold_splits["e_val"],
                                                      eclipse_fold_splits["test"], eclipse_fold_splits["e_test"])
    if not os.path.exists(os.path.join(model.eclipse.save_path, "model.pkl")):
        print("Beginning eclipse model training")
        model.eclipse.train(x_train, y_train, x_val, y_val)
    else:
        print("Found saved eclipse weights, restoring")
        model.eclipse = model.eclipse.load_model()
        model.eclipse.save_path = os.path.join(model.save_path, "eclipse")
    print("Evaluating eclipse on test set")
    model.eclipse.test(x_test, y_test)

    # Train the experts
    train_test_expert(model.experts, experts_train, experts_val, experts_test, -1, ckpt_path,
                      "expert", args)

    if args.debug:
        x_test_raw = x_test_raw[:20]
        y_test_raw = y_test_raw[:20]
        x_val_raw = x_val_raw[:20]
        y_val_raw = y_val_raw[:20]

    testing = [("test", x_test_raw, y_test_raw), ("val", x_val_raw, y_val_raw)]
    if args.test:
        testing.pop()

    for t_type, x, y in testing:
        if args.test:
            t_type = args.test
        print(f"Testing MoE on {t_type} set")
        print("Finished training expert models\nTesting with no enzyme information available")
        thresholds = get_thresholds(value_type=set)
        test_no_enzyme, pred_enzymes = model.smiles_to_smiles_inf([r.split(">>")[0] for r in x])
        no_enzyme_score = process_compare_reactions(x, test_no_enzyme, thresholds)
        no_enzyme_recall, no_enzyme_precision, no_enzyme_area = sort_recall_precision(no_enzyme_score["recall"],
                                                                                      no_enzyme_score["precision"])
        no_enzyme_score["predictions_enzymes"] = {x[i].split(">>")[0]: pred_enzymes[i] for i in range(len(x))}
        with open(f"{result_path}/{t_type}_output_no_enzyme.json", "w") as out_file:
            json.dump(no_enzyme_score, out_file, indent=4)
        print("Testing with enzyme information available")
        test_enzyme, _ = model.smiles_to_smiles_inf([r.split(">>")[0] for r in x], ec_classes=y)
        enzyme_score = process_compare_reactions(x, test_enzyme, thresholds)
        enzyme_recall, enzyme_precision, enzyme_area = sort_recall_precision(enzyme_score["recall"],
                                                                             enzyme_score["precision"])
        with open(f"{result_path}/{t_type}_output_enzyme.json", "w") as out_file:
            json.dump(enzyme_score, out_file, indent=4)
        pr_curves = [[no_enzyme_recall, no_enzyme_precision, f"No Enzyme AUC: {no_enzyme_area:.3f}"], [enzyme_recall, enzyme_precision, f"Enzyme AUC: {enzyme_area:.3f}"]]
        plot_pr_curve([], [], 0, "", f"{result_path}/{t_type}_pr.png", extra_pr=pr_curves)
    with open(f"{result_path}/tokens.json", "w") as token_file:
        json.dump(tokenizer, token_file, indent=4)
    with open(f"{result_path}/config.json", "w") as c_file:
        json.dump(config, c_file, indent=4)
    return


def train_many(args):
    search_space = {"seed": list(range(2)), "use_enzyme": [False, True]}
    search_space = expand_search_space(search_space)
    model_class, config = setup_model(args)
    for search in search_space:
        for k, v in search.items():
            if k in vars(args):
                setattr(args, k, v)
            elif k not in config:
                raise ValueError(f"Search space key {k} not in args")
        for k, v in config.items():
            if k not in search:
                search[k] = v
        train(args, model_class, search)
        torch.cuda.empty_cache()


def product_main():
    arguments = get_arguments()
    if arguments.train_many:
        train_many(arguments)
    else:
        train_one(arguments)


if __name__ == "__main__":
    product_main()
