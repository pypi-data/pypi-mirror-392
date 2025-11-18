# Eclipse - Enzyme Class Learning and Interaction Prediction SystEm
This repository gives the code for the paper "Predicting Enzyme-Compound Interactions for Enzyme-Catalysed Reactions".

# Installation
For the majority of use cases, such as simply performing inference with out-of-the-box ECLIPSE, CUDA is **not** required.

## Without CUDA support
1. `pip install chem-eclipse[cpu]` when installing from pip or `uv sync --extra cpu` if cloning the repository
2. Download the data. All files referenced are available [here](https://doi.org/10.5281/zenodo.17489235):
   1. Download the `ecmap.csv` such that the directory path `data/ecmap.csv` exists.
   2. Download the `results.zip` file and unzip it so the path `results/TransformerModel/uspto_rdkit/` exists.
   3. Run `prepare_envipath_data` to download envipath data, this may take a while.

## With CUDA support

The CUDA implementation is highly recommended if you want to perform product prediction. 
It is also recommended if you are wanting to train a large number of configurations on powerful GPUs.

We recommend using [UV](https://docs.astral.sh/uv/getting-started/installation/) for dependency management with CUDA. 
It ensures the correct torch distribution is selected for your system.
You can make the virtual environment with UV using `uv venv --python 3.12`.
1. Install CUDA toolkit 12.8 [here](https://developer.nvidia.com/cuda-12-8-0-download-archive)
2. `uv pip install chem-eclipse[cuda] --torch-backend=auto` when installing from pip or `uv sync --extra cuda` if cloning the repository.
3. `python -m cupyx.tools.install_library --cuda 12.x --library cutensor`
4. Download the data. All files referenced are available [here](https://doi.org/10.5281/zenodo.17489235):
   1. Download the `ecmap.csv` file such that the directory path `data/ecmap.csv` exists.
   2. Download the `results.zip` file and unzip it so the path `results/TransformerModel/uspto_rdkit/` exists.
   3. Run `prepare_envipath_data` to download envipath data, this may take a while.
5. Restart system

## Data
***NOTE:*** The installation steps includes getting the data, this is for manually getting the data.

The ECMap dataset is available [here](https://doi.org/10.5281/zenodo.17489235) as `ecmap.csv`.
EnviPath data can be downloaded using `chem_eclipse.utils.prepare_envipath_data`.

# Running Your Own Experiments

## Inference on your own dataset
If you have a dataset with no EC numbers that you would like to predict EC numbers on use the following steps:
1. Create a csv file `YOUR_DATASET_NAME.csv`. It only needs one column, rdkit_reactants, containing the SMILES of compounds you wish to predict.
2. Run the command `oob_inference --test path/to/YOUR_DATASET_NAME.csv`.

This will use our out-of-the-box hierarchy ECLIPSE configuration. They will be trained on first run but loaded thereafter. 
We have two available configurations one trained on the ECMap dataset and one on the BBD dataset. 
You can choose between these with the command line argument `--data-name [ecmap OR bbd]`.

The predictions will be saved into `results/summary/YOUR_DATASET_NAME_pred.json`.

## Training with your own dataset
If you have a dataset you would like to train and test with please use the following steps:
1. Create a csv file `YOUR_DATASET_NAME.csv`. The csv file should contain two named columns for `ECLIPSETrain.py` and three for `ProductPredictionTrain.py`:
   - `ECLIPSETrain.py`: ec_num and rdkit_reactants
   - `ProductPredictionTrain.py`: ec_num, rdkit_reactants, rdkit_reaction
2. Run your desired experiment with `--data-name path/to/YOUR_DATASET_NAME.csv`

# Recreate Experiments
Instructions for re-running experiments in the paper.
## Train ECLIPSE
To train ECLIPSE model call `chem_eclipse.ECLIPSETrain.eclipse_train_main` in code or `eclipse_train_main` from the terminal. 

Use the command line argument `--eclipse-type` to choose between Flat (f) and Hierarchy (h) ECLIPSE, the default is Hierarchy (h). 
For example, to run with Flat ECLIPSE `python ECLIPSETrain.py -tm --eclipse-type f`.
This will create a `.csv` file in `results/summary/` containing the results of each configuration on each seed.

## Soil and Sludge Inference
To run inference on soil and sludge run `chem_eclipse.ECLIPSEInference.eclipse_inference_main` in code 
or `eclipse_inference_main` from the command line with the command line argument `--test ['soil' or 'sludge']`.

## Train Product Prediction
Training the product prediction model with EC numbers is done with `chem_eclipse.ProductPredictionTrain.product_main` from code 
or `product_main` from the command line.

If the file `results/summary/hierarchy.csv` exists the best ECLIPSE for the current seed (command line argument `--seed X`) will be used.
Otherwise, a new ECLIPSE will be trained.

## BEC-Pred
The models we trained with our modified BEC-Pred code are available [here](https://doi.org/10.5281/zenodo.17489235) under `bec_pred_models.zip`.
See the fork of BEC-Pred available [here](https://github.com/MyCreativityOutlet/BEC-Pred) for the modifications we made.

## Plotting Figures and Tables
For plotting tables call `chem_eclipse.ModelAnalysis.recreate_tables_figures` from code or `recreate_tables_figures` from the command line. 
This assumes that the following files exist:
- `results/summary/hierarchy.csv`
- `results/summary/flat.csv`
- `results/summary/bbd_final/*` (from `ECLIPSEInference.py`)
- `results/summary/ecmap_final/*` (from `ECLIPSEInference.py`)
- *Optional*: `results/summary/bec_pred.csv`.

***NOTE:*** The runtime analysis and Figure 3 creation is done in `chem_eclipse.ECLIPSERuntimeAnalysis.runtime_main`

# Customising ECLIPSE
Here are some simple ways you can customise or extend ECLIPSE.

## ECLIPSE Search Space
To change the parameters that ECLIPSE will search over pass the named argument `search_space` to `chem_eclpise.ECLIPSETrain.eclipse_train_main` with the command line argument `-tm`.
`search_space` should be a dictionary where the keys are strings and values are lists.
Valid parameters include:
- n_estimators (estimators in xgboost)
- max_depth (maximum depth in xgboost)
- n_chains (for flat ECLIPSE only)
- seed (random seed for splitting)
- radius (for the morgan fingerprint)
- n_bits (for the morgan fingerprint)

## Command Line Arguments
Here are all the command line arguments that affect ECLIPSE
- --data-name \[string\] (Which dataset to use for training, bbd, ecmap)
- --test \[string\] (Which dataset to use for testing)
- --eclipse-type \[string\] (Whether to train the H or F ECLIPSE)
- --split-path \[string\] (Predetermined split file, a dictionary with train, val and test keys each containing a list of SMILES)
- --train-many or -tm (Whether to train many models with the search space or one configuration)
- --workers \[int\] (The number of CPUs used during training)
- --gpu (Whether to use GPU for XGBoost)

## Custom Configuration
You can call `chem_eclipse.ECLIPSETrain.train` to train with a custom configuration. 
This also requires the command line argument to be parsed, these can be retrieved by calling `chem_eclipse.utils.get_arguments`.
The configuration should be a dictionary and can contain the following keys:
- n_estimators (estimators in xgboost)
- max_depth (maximum depth in xgboost)
- n_chains (for flat ECLIPSE only)
- radius (for the morgan fingerprint)
- n_bits (for the morgan fingerprint)
- ec_lvl (maximum level of the EC number that will be considered)
- ec_min (minimum number of examples of an EC number for it to be considered a class)