import json
import os.path
import shutil
from importlib import resources
import pandas as pd
import torch
from chem_eclipse.models.ECLIPSEModel import ECLIPSEModel
from chem_eclipse.models.TransformerModel import TransformerModel
from tqdm import tqdm
from chem_eclipse.utils import encode_mol, get_moe_version


class ECLIPSEProdModel:
    def __init__(self, config, vocab, ec_vocab, p_args, train_steps):
        super().__init__()
        self.char_to_i, self.i_to_char = vocab
        self.args = p_args
        self.ec_to_i = ec_vocab
        self.i_to_ec = {v: k for k, v in ec_vocab.items()}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.pad_id = self.char_to_i["[nop]"]
        self.topk_ec = config.get("topk_ec", 3)
        self.moe_config = config
        self.save_path = os.path.join("results", "ECLIPSEProdModel", get_moe_version(p_args, config))
        os.makedirs(self.save_path, exist_ok=True)
        os.makedirs(os.path.join(self.save_path, "eclipse"), exist_ok=True)
        tolerance = None
        if os.path.exists(p := "results/summary/hierarchy.csv"):
            eclipse_results = pd.read_csv(p)
            eclipse_results = eclipse_results[(eclipse_results["seed"] == p_args.seed) & (eclipse_results["data_name"] == p_args.data_name)]
            if len(eclipse_results) > 0:
                eclipse_results = eclipse_results.loc[(eclipse_results["val_f1"].idxmax())]
                base_path = eclipse_results.path.replace("\\", "/")
                with open(os.path.join(base_path, "config.json")) as c_file:
                    eclipse_config = json.load(c_file)
                shutil.copy(os.path.join(base_path, "config.json"),
                            f"results/ECLIPSEProdModel/{get_moe_version(p_args, config)}/eclipse/config.json")
                shutil.copy(os.path.join(base_path, "model.pkl"),
                            f"results/ECLIPSEProdModel/{get_moe_version(p_args, config)}/eclipse/model.pkl")
                tolerance = eclipse_results.tolerance
            else:
                with resources.files("chem_eclipse.models").joinpath("ECLIPSEModel_config.json").open("r") as c_file:
                    eclipse_config = json.load(c_file)
        else:
            with resources.files("chem_eclipse.models").joinpath("ECLIPSEModel_config.json").open("r") as c_file:
                eclipse_config = json.load(c_file)
        self.eclipse = ECLIPSEModel(self.ec_to_i, eclipse_config, p_args,
                              save_path=f"results/ECLIPSEProdModel/{get_moe_version(p_args, config)}/eclipse",
                              tolerance=tolerance, device="cuda" if p_args.gpu else 'cpu')
        self.experts = TransformerModel(config, vocab, p_args, train_steps=train_steps,
                                        save_path=f"results/ECLIPSEProdModel/{get_moe_version(p_args, config)}/expert")

    def smiles_to_smiles_inf(self, smiles, ec_classes=None):
        with torch.no_grad():
            self.experts.eval()
            smiles_enc = [encode_mol(s, self.char_to_i, self.args, enclose=False) for s in smiles]
            bad_smiles = []
            for i, enc in enumerate(smiles_enc):
                if enc is None:
                    bad_smiles.append(i)
            if ec_classes is None:
                ec_classes = []
                bad_set = set(bad_smiles)
                predictions = self.eclipse.predict([smiles[i] for i in range(len(smiles)) if i not in bad_set])
                for pred in predictions:
                    ec_classes.append([(e, 0) for e in pred[:self.topk_ec]])
                for bad_i in bad_smiles:
                    ec_classes.insert(bad_i, -1)
            else:
                ec_classes = [[(e, 0)] if e != -1 else -1 for e in ec_classes]
            grouping = {}
            for i, ec_class in enumerate(ec_classes):
                if ec_class != -1:
                    for ec, prob in ec_class:
                        grouping.setdefault(ec, []).append((i, prob))
            pred_smiles = [[] for _ in range(len(smiles))]
            pred_proba = [[] for _ in range(len(smiles))]
            self.experts.to(self.device)
            for ec_class, ids in tqdm(grouping.items(), desc="Predicting SMILES"):
                if self.moe_config.get("use_enzyme", True):
                    e_smiles = [f"{smiles[i]}>{ec_class if ec_class != 'other' else ''}" for i, k in ids]
                else:
                    e_smiles = [smiles[i] for i, k in ids]
                predicted_smiles, predicted_probabilities = self.experts.smiles_to_smiles_inf(e_smiles, num_beams=3,
                                                                                              batch_size=self.args.batch_size // 2)
                for idx, (original_idx, _) in enumerate(ids):
                    pred_smiles[original_idx].extend(predicted_smiles[idx])
                    pred_proba[original_idx].extend(predicted_probabilities[idx])
            self.experts.to("cpu")
            sorted_smiles = []
            sorted_probabilities = []
            for bad_i in bad_smiles:
                pred_smiles[bad_i] = [""]
                pred_proba[bad_i] = [float("-inf")]
            for smiles, probas in zip(pred_smiles, pred_proba):
                if len(smiles) == 0:
                    smiles = [""]
                    probas = [float("-inf")]
                sorted_pred = sorted(zip(smiles, probas), key=lambda x: x[1], reverse=True)
                smiles, probas = zip(*sorted_pred)
                sorted_smiles.append(list(smiles))
                sorted_probabilities.append(list(probas))
        return (sorted_smiles, sorted_probabilities), ec_classes

    def __call__(self, src, ec_classes=None):
        return self.smiles_to_smiles_inf(src, ec_classes)
