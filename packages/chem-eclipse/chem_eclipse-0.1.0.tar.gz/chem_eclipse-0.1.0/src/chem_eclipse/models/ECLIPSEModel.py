import json
import math
import numpy as np
from sklearn.base import clone, BaseEstimator
from sklearn.exceptions import NotFittedError
import time
import os
from joblib import Parallel, delayed
from sklearn.multioutput import ClassifierChain
from tqdm import tqdm
from rdkit import Chem, RDLogger
from rdkit.Chem import rdFingerprintGenerator
import joblib
from chem_eclipse.hiclass.MultiLabelLocalClassifierPerNode import MultiLabelLocalClassifierPerNode
from xgboost import XGBClassifier
from chem_eclipse.utils import hierarchy_eclipse_eval, sort_recall_precision, plot_pr_curve, convert_eclipse_type


class ECLIPSEModel:
    def __init__(self, ec_to_i, config, args, **kwargs):
        self.radius = config.get("radius", 2)
        self.config = config
        self.args = args
        self.n_bits = config.get("n_bits", 2048)
        self.fp_cache = {}
        self.fp_cache_path = os.path.join(f"data/{args.data_name}/{self.radius}_{self.n_bits}_fps.json")
        self.fp_updated = False
        self.tolerance = kwargs.get("tolerance", None)
        self.tolerance_f1 = {}
        if os.path.exists(self.fp_cache_path):
            with open(self.fp_cache_path) as f_file:
                self.fp_cache = json.load(f_file)
        else:
            os.makedirs(os.path.dirname(self.fp_cache_path), exist_ok=True)
        self.n_estimators = config["n_estimators"]
        self.max_depth = config["max_depth"]
        self.label_format = convert_eclipse_type(args.eclipse_type)
        self.ec_to_i = ec_to_i
        self.i_to_ec = {i: e for e, i in self.ec_to_i.items()}
        self.device = kwargs.get("device", "cuda")
        estimator = XGBClassifier(objective="binary:logistic", n_estimators=self.n_estimators,
                                  max_depth=self.max_depth, random_state=args.seed, device=self.device, n_jobs=args.workers)
        if self.label_format == "hierarchy":
            self.model = CuPyMultiLabelLocalClassifierPerNode(estimator, n_jobs=args.workers) # if self.device != "cuda" else 1)
        elif self.label_format == "flat":
            self.model = ECC(estimator, n_chains=config["n_chains"], n_jobs=args.workers) # if self.device != "cuda" else 1)
        else:
            raise ValueError(f"Unknown label format: {self.label_format}")
        self.save_path = kwargs.get("save_path", None)
        if self.save_path is None:
            self.save_path = f"results/ECLIPSEModel/{self.get_version()}"
        if not kwargs.get("no_folder", False):
            os.makedirs(self.save_path, exist_ok=True)

    def smiles_to_fingerprint(self, smiles):
        if smiles in self.fp_cache:
            return self.fp_cache[smiles]
        RDLogger.DisableLog('rdApp.*')
        mol = Chem.MolFromSmiles(smiles)
        finger_gen = rdFingerprintGenerator.GetMorganGenerator(radius=self.radius, fpSize=self.n_bits)
        if mol is None:
            return None
        fp = finger_gen.GetFingerprint(mol)
        arr = list(fp)
        self.fp_cache[smiles] = arr
        self.fp_updated = True
        return arr

    def get_version(self):
        version = f"{self.args.data_name}_{self.n_estimators}_{self.max_depth}_{self.config['ec_min']}_{self.config['ec_lvl']}"
        if self.label_format == "flat":
            version += f"_{self.label_format}_{self.config['n_chains']}"
        version += f"_{self.args.seed}"
        return version

    def train(self, x_train, y_train, x_val, y_val):
        x_train_enc, y_train_enc, x_train = self.process_x_y(x_train, y_train)
        print("Beginning model training")
        if self.device == "cuda":
            import cupy as cp
            x_train_enc = cp.array(x_train_enc)
            if self.label_format != "hierarchy":
                y_train_enc = cp.array(y_train_enc)
        start_time = time.time()
        self.model.fit(x_train_enc, y_train_enc)
        print(f"Finished model training in {time.time() - start_time:.1f} seconds, saving and evaluating on val data")
        self.save_model()
        if x_val and y_val:
            self.test(x_val, y_val, "val")
        return self

    def process_x_y(self, x, y):
        fingerprints, enzyme_h, good_smiles = [], [], []
        for i, smiles in enumerate(tqdm(x, desc="Getting fingerprints")):
            fingerprint = self.smiles_to_fingerprint(smiles)
            if fingerprint is not None:
                fingerprints.append(fingerprint)
                if self.label_format == "hierarchy":
                    enzyme_h.append(self.one_hot_to_hierarchy(y[i]))
                elif self.label_format == "flat":
                    enzyme_h.append(y[i])
                else:
                    raise ValueError(f"Unknown label format: {self.label_format}")
                good_smiles.append(smiles)
        if self.fp_updated:
            with open(self.fp_cache_path, "w") as f_file:
                json.dump(self.fp_cache, f_file)
        return np.array(fingerprints), np.array(enzyme_h, dtype=object if self.label_format == "hierarchy" else None), good_smiles

    def one_hot_to_hierarchy(self, one_hot):
        ec_lvls = []
        for j in np.nonzero(one_hot)[0]:
            ec_split = self.i_to_ec[j.item()].split(".")
            ec_lvls.append([".".join(ec_split[:lvl]) for lvl in range(1, len(ec_split) + 1)])
        return ec_lvls

    def test(self, x_test, y_test, test_type="test", force_rerun=False):
        save_path = os.path.join(self.save_path, f"{test_type}_tol_output.json")
        if os.path.exists(save_path) and not force_rerun:
            with open(save_path) as f:
                return json.load(f)
        tolerances = [0.0, 0.01, 0.025, 0.1, 0.4]
        x_test_enc, y_test_enc, x_test = self.process_x_y(x_test, y_test)
        if self.label_format == "flat":
            y_test_enc = [self.one_hot_to_hierarchy(y) for y in y_test_enc]
        if self.device == "cuda":
            import cupy as cp
            x_test_enc = cp.array(x_test_enc)
        tolerance_reports = {}
        for tolerance in tolerances:
            predictions = self.model.predict(x_test_enc, tolerance=tolerance)
            if self.label_format == "flat":
                predictions = [self.one_hot_to_hierarchy(p) for p in predictions]
            report = hierarchy_eclipse_eval(x_test, y_test_enc, predictions)
            if test_type == "val":
                self.tolerance_f1[tolerance] = report["f1"]
                self.tolerance = max(self.tolerance_f1, key=lambda x: self.tolerance_f1[x])
                self.config["tolerance"] = self.tolerance
            tolerance_reports[tolerance] = hierarchy_eclipse_eval(x_test, y_test_enc, predictions)
        precision = {}
        recall = {}
        for tolerance in tolerances:
            precision[tolerance] = tolerance_reports[tolerance]["precision"]
            recall[tolerance] = tolerance_reports[tolerance]["recall"]
        recall, precision, _ = sort_recall_precision(recall, precision)
        plot_pr_curve([], [], 0, test_type, path=f"{self.save_path}/{test_type}_pr.png",
                      extra_pr=[[recall, precision, "eclipse"]], xmin=0.7, ymin=0.2)
        with open(save_path, "w") as f:
            json.dump(tolerance_reports, f)
        return tolerance_reports

    def predict(self, smiles, tolerance=None):
        if tolerance is None:
            tolerance = self.tolerance if self.tolerance is not None else 0.0
        RDLogger.DisableLog('rdApp.*')
        fps = []
        for s in tqdm(smiles, desc="Processing SMILES"):
            f_print = self.smiles_to_fingerprint(s)
            if f_print is not None:
                fps.append(f_print)
            else:
                raise ValueError(f"Invalid SMILES: {s}")
        if self.device == "cuda":
            import cupy as cp
            fps = cp.array(fps)
        else:
            fps = np.array(fps)
        raw_pred = self.model.predict(fps, tolerance=tolerance)
        if self.label_format == "flat":
            raw_pred = [self.one_hot_to_hierarchy(p) for p in raw_pred]
        elif self.label_format == "hierarchy":
            raw_pred = raw_pred[:, :, -1].tolist()
            raw_pred = [[r for r in pred if r != ""] for pred in raw_pred]
        return raw_pred

    def save_model(self):
        """
        Save the trained model to disk.
        """
        joblib.dump(self.model, os.path.join(self.save_path, "model.pkl"), compress=True)
        with open(os.path.join(self.save_path, "config.json"), "w") as c_file:
            json.dump(self.config, c_file, indent=4)

    def load_model(self, path=None):
        """
        Load a trained model from disk.
        """
        _path = self.save_path if path is None else path
        with open(os.path.join(_path, "config.json")) as c_file:
            config = json.load(c_file)
        loaded = ECLIPSEModel(self.ec_to_i, config, self.args, device=self.device, tolerance=self.tolerance)
        if not path:
            loaded.save_path = self.save_path
        loaded.model = joblib.load(os.path.join(_path, "model.pkl"))
        loaded.tolerance = config.get("tolerance", None)

        if self.label_format == "hierarchy":
            for _, est in loaded.model.hierarchy_.nodes(data="classifier"):
                if isinstance(est, XGBClassifier):
                    est.set_params(device=self.device)
        elif self.label_format == "flat":
            for chain in loaded.model.chains:
                for estimator in chain.estimators_:
                    if isinstance(estimator, XGBClassifier):
                        estimator.set_params(device=self.device)
        return loaded


class ECC(BaseEstimator):
    def __init__(self, model, n_chains=10, n_jobs=1):
        """
        Initialize the Ensemble of Classifier Chains (ECC).

        Parameters:
        - model: Base model to be used in each classifier chain (e.g., RandomForest, SVC, etc.).
        - n_chains: Number of chains in the ensemble (default: 10).
        - n_jobs: Number of parallel jobs (default: 1). If 1, no parallelization will be used.
        """
        self.model = model
        self.n_chains = n_chains
        self.n_jobs = n_jobs
        self.chains = None

    def fit(self, X, Y):
        """
        Train the ensemble of classifier chains.

        Parameters:
        - X: Feature matrix (DataFrame or array-like).
        - Y: Multi-label targets (DataFrame or array-like).
        """
        if len(X) != len(Y):
            raise ValueError("The number of samples in X and Y must be the same.")

        # Initialize chains with random order and independent models
        self.chains = [CuPySafeChain(clone(self.model), order="random") for _ in range(self.n_chains)]
        if self.n_jobs > 1:
            self.chains = Parallel(n_jobs=min(self.n_jobs, len(self.chains)),
                                   batch_size=math.ceil(len(self.chains) / self.n_jobs),
                                   verbose=11)(delayed(chain.fit)(X, Y) for chain in self.chains)
        else:
            for chain in tqdm(self.chains):
                chain.fit(X, Y)

    def predict_proba(self, X):
        """
        Compute the label probabilities for the input data.

        Parameters:
        - X: Input feature matrix (DataFrame or array-like).

        Returns:
        - Array of probabilities for each label.
        """
        if self.chains is None:
            raise NotFittedError('Model has not been fitted yet.')

        # Parallelized prediction probabilities
        if self.n_jobs > 1:
            predictions = Parallel(n_jobs=min(self.n_jobs, len(self.chains)),
                                   batch_size=math.ceil(len(self.chains) / self.n_jobs),
                                   verbose=11)(delayed(chain.predict_proba)(X) for chain in self.chains)
        else:
            predictions = [chain.predict_proba(X) for chain in tqdm(self.chains, desc="Predicting with chains")]

        return np.mean(predictions, axis=0)

    def predict(self, X, tolerance=None):
        """
        Make binary predictions based on the probability threshold.

        Parameters:
        - X: Input feature matrix (DataFrame or array-like).
        - tolerance: Probability threshold to convert probabilities to binary (default: 0.5).

        Returns:
        - Array of binary predictions for each label.
        """
        _tolerance = tolerance

        probas = self.predict_proba(X)
        highest_probabilities = np.max(probas, axis=1, keepdims=True)
        predictions = (probas >= highest_probabilities - tolerance).astype(int)
        return predictions

    def predict_cardinality(self, X, Y_train):
        """
        Make binary predictions using a threshold based on the label cardinality from the training set.

        Parameters:
        - X: Input feature matrix (DataFrame or array-like).
        - Y_train: Training multi-label target (to calculate cardinality).

        Returns:
        - Array of binary predictions for each label based on cardinality.
        """
        cardinality = Y_train.sum(axis=1).mean() / Y_train.shape[1]
        probas = self.predict_proba(X)
        return (probas >= cardinality).astype(int)


class CuPySafeChain(ClassifierChain):
    def _validate_data(self, X, y=None, **kwargs):
        # Avoid enforcing NumPy conversion
        if y is None:
            return X
        return X, y


class CuPyMultiLabelLocalClassifierPerNode(MultiLabelLocalClassifierPerNode):
    def _validate_data(self, X, y=None, **kwargs):
        if y is None:
            return X
        return X, y
