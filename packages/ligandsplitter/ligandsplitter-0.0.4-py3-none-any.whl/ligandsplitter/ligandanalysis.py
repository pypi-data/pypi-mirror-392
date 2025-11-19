"""Provide the primary functions."""
import sys, os
import numpy as np
import re
from rdkit import Chem
from rdkit.Chem import Descriptors, Crippen, Lipinski
import pandas as pd
from sklearn.model_selection import RandomizedSearchCV, train_test_split, cross_val_score, cross_validate
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.compose import ColumnTransformer, make_column_transformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
import xgboost as xgb
from .basefunctions import LigandVariables

vars = LigandVariables()

def group_idxes_from_mol(lig, renumber = False):
    """
    Get atom indices of functional groups in a ligand molecule.

    Parameters
    ----------
    lig : RDKIT molecule
        Ligand of interest.

    Returns
    -------
    match_indexes : dict
        Dictionary of functional groups and their corresponding atom indexes in the ligand.
    """
    match_indexes = {}
    mol = lig
    if renumber:
        mol_neworder = tuple(zip(*sorted([(j, i) for i, j in enumerate(Chem.CanonicalRankAtoms(mol))])))[1]
        mol_renum = Chem.RenumberAtoms(mol, mol_neworder)
    else:
        mol_renum = mol
    for j in vars.functional_groups:
        k = Chem.MolFromSmarts(j)
        if mol_renum.HasSubstructMatch(k):
            idxes = mol_renum.GetSubstructMatches(k)
            dict_keys = list(match_indexes.keys())
            for index in idxes:
                for subind in index:
                    subind_string = str(subind)
                    if subind_string in dict_keys:
                        temp_match = match_indexes[subind_string]
                        match_indexes[subind_string] = temp_match.append(vars.functional_groups_dict[j])
                    else:
                        match_indexes[subind_string] = [vars.functional_groups_dict[j]]
    return match_indexes

def oral_bioactive_classifier(data, method = ""):
    """
    Determine the importance of ligand features in whether they are orally bioactive or not using a Random Forest Classifier.
    
    Parameters
    ----------
    data : dataframe
        Data containing physical properties of ligand of interest.
    method : String
        Method to use for analysis. Options are "LRO5", "Ghose", or "Veber".

    Returns
    -------
    imps : dataframe
        Dataframe containing feature importances of the model.
    results_dict : dict
        Dictionary containing predicted orally bioactive values for ligands with missing data (included by user).
    """
    results_dict = {}

    # get feature and target variables
    names = data[data["orally_bioactive"].isna()]["filename_hydrogens"].tolist()
    features = data[data["orally_bioactive"].notna()]
    features_na = data[data["orally_bioactive"].isna()]
    # drop unneeded columns based on method
    # Lipinski's Rule of 5: MW <= 500, logP <= 5, H-bond donors <= 5, H-bond acceptors <= 10
    # drop mol_refractivity, rotatable_bonds, polar_surface_area for LRO5
    if method == "LRO5":
        features = features.drop(columns = ["filename_hydrogens", "smiles", "mol_refractivity", "rotatable_bonds", "polar_surface_area", "orally_bioactive", "mol"])
        features_na = features_na.drop(columns = ["filename_hydrogens", "smiles", "mol_refractivity", "rotatable_bonds", "polar_surface_area", "orally_bioactive", "mol"])
    # Ghose filter: 160 <= MW <= 480, -0.4 <= logP <= 5.6, 40 <= molar refractivity <= 130, 20 <= atoms <= 70
    # drop rotatable_bonds, polar_surface_area for Ghose
    elif method == "Ghose":
        features = features.drop(columns = ["filename_hydrogens", "smiles", "rotatable_bonds", "polar_surface_area", "orally_bioactive", "mol"])
        features_na = features_na.drop(columns = ["filename_hydrogens", "smiles", "rotatable_bonds", "polar_surface_area", "orally_bioactive", "mol"])
    # Veber's rule: rotatable_bonds <= 10, polar_surface_area <= 140
    # drop no additional features for Veber
    elif method == "Veber":
        features = features.drop(columns = ["filename_hydrogens", "smiles", "orally_bioactive", "mol"])
        features_na = features_na.drop(columns = ["filename_hydrogens", "smiles", "orally_bioactive", "mol"])
    else:
        print("Please provide a valid method: LRO5, Ghose, or Veber.")
    
    # target is orally_bioactive column
    target = data[data["orally_bioactive"].notna()]["orally_bioactive"]

    # define training and testing data
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size = 0.2)
    rf_c = RandomForestClassifier()
    rf_c.fit(X_train, y_train)
    scores_rf_c = cross_validate(rf_c, X_train, y_train, return_train_score=True)
    print(f"Initial cross-validation fit time: {scores_rf_c['fit_time']}")
    print(f"Initial cross-validation score time: {scores_rf_c['score_time']}")
    print(f"Initial cross-validation training scores: {scores_rf_c['train_score']}")
    print(f"Initial cross-validation testing scores: {scores_rf_c['test_score']}")

    # hyperparameter optimization
    print("Starting hyperparameter optimization...")
    rf_param_grid = {
        "max_depth": [1, 5, 10, 15, 20],
        "max_features": [1, 5, 10, 15, 20],
        "min_samples_split": [10, 20, 30, 40, 50],
        "min_samples_leaf": [5, 10, 15, 20]
    }
    rf_random_search = RandomizedSearchCV(
        RandomForestClassifier(), param_distributions=rf_param_grid, n_jobs=-1, n_iter=10, cv=5, random_state=123
    )
    print("Done!")

    # create and deploy optimized model
    print("Fitting optimized model...")
    rf_random_search.fit(X_train, y_train)
    optimized_rf_c = pd.DataFrame(rf_random_search.cv_results_)[["mean_test_score","param_max_depth","param_max_features", "param_min_samples_split", "param_min_samples_leaf", "mean_fit_time","rank_test_score",]].set_index("rank_test_score").sort_index().T
    max_depth_val = int(optimized_rf_c.iloc[1,1])
    max_features_val = int(optimized_rf_c.iloc[1,2])
    min_sample_split_val = int(optimized_rf_c.iloc[1,3])
    min_samples_leaf_val = int(optimized_rf_c.iloc[1,4])
    rf_optimal = RandomForestClassifier(max_depth = max_depth_val, max_features = max_features_val, min_samples_split = min_sample_split_val, min_samples_leaf = min_samples_leaf_val)
    rf_optimal.fit(X_train, y_train)
    score = rf_optimal.score(X_test, y_test)
    print(f"Optimized model test score: {score}")
    predictions = rf_optimal.predict(features_na)
    for index, row in features_na.iterrows():
        print(f"Predicted orally bioactive value for {names[index]}: {predictions[index]}")
        results_dict[names[index]] = predictions[index]

    # obtain feature importance
    feature_names = list(X_train.columns)
    data = {
        "Importance": rf_optimal.feature_importances_,
    }
    imps = pd.DataFrame(data=data, index=feature_names,).sort_values(by="Importance", ascending=False)[:10]
    return imps, results_dict

def interaction_regressor(data, quiet = True):
    """
    Determine the importance of ligand features in determining binding affinity.
    
    Parameters
    ----------
    data : dataframe
        Data containing docking information between ligand/s of interest and receptor.

    Returns
    -------
    imps : dataframe
        Dataframe containing feature importances of the model.
    """

    features = data.drop(columns = ["Score", "Frame"])
    if "Ligand" in features.columns:
        features = features.drop(columns = ["Ligand"])
        
    target = data["Score"]
    shape = features.shape[0]
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size = 0.2)
    if X_train.shape[0] < 10:
        print("Docking data too small to perform machine learning analysis on.")
        imps_rf, imps_xgb = "N/A", "N/A"
        return imps_rf, imps_xgb
    
    # initial training
    xgb_model = xgb.XGBRegressor()
    xgb_model.fit(X_train, y_train)
    rf_r = RandomForestRegressor()
    rf_r.fit(X_train, y_train)

    scores_rf_r = cross_validate(rf_r, X_train, y_train, return_train_score=True)
    scores_xgb_r = cross_validate(xgb_model, X_train, y_train, return_train_score=True)
    
    if quiet == False:
        print(f"Initial Random Forest cross-validation fit time: {scores_rf_r['fit_time']}")
        print(f"Initial Random Forest cross-validation score time: {scores_rf_r['score_time']}")
        print(f"Initial Random Forest cross-validation training scores: {scores_rf_r['train_score']}")
        print(f"Initial Random Forest cross-validation testing scores: {scores_rf_r['test_score']}")

        print(f"Initial XGBoost cross-validation fit time: {scores_xgb_r['fit_time']}")
        print(f"Initial XGBoost cross-validation score time: {scores_xgb_r['score_time']}")
        print(f"Initial XGBoost cross-validation training scores: {scores_xgb_r['train_score']}")
        print(f"Initial XGBoost cross-validation testing scores: {scores_xgb_r['test_score']}")

    # hyperparameter optimization
    print("Starting hyperparameter optimization...")
    if shape > 100:
        rf_param_grid = {
            "max_depth": [1, 5, 10, 15, 20],
            "max_features": [1, 5, 10, 15, 20],
            "min_samples_split": [10, 20, 30, 40, 50],
            "min_samples_leaf": [5, 10, 15, 20]
        }
        xgb_param_grid = {
            "max_depth": [1, 5, 10, 15, 20],
            "colsample_bynode": [0.3, 0.5, 0.7, 0.9],
            "min_child_weight": [5, 10, 15, 20]
        }
    else:
        # if dataset is smaller than 50 samples, adjust hyperparameter ranges
        calc_min_sample_depth = int(shape * 0.5)
        calc_min_sample_other_val = int(shape * 0.75)

        float_step = calc_min_sample_depth/5
        float_weight_step = (calc_min_sample_other_val - 5)/5
        depth_val_step = int(float_step) if float_step > 1 else 1
        child_weight_val_step = int(float_weight_step) if float_weight_step > 1 else 1
        depth_vals = [x for x in range(1, calc_min_sample_depth + 1, depth_val_step)]
        child_weight_vals = [x for x in range(5, calc_min_sample_other_val + 1, child_weight_val_step)]
        
        rf_param_grid = {
            "max_depth": depth_vals,
            "max_features": [0.3, 0.5, 0.7, 0.9],
            "min_samples_split": [0.3, 0.5, 0.7, 0.9],
            "min_samples_leaf": [0.3, 0.5, 0.7, 0.9]
        }
        xgb_param_grid = {
            "max_depth": depth_vals,
            "colsample_bynode": [0.3, 0.5, 0.7, 0.9],
            "min_child_weight": child_weight_vals
        }
    rf_random_search = RandomizedSearchCV(RandomForestRegressor(), param_distributions=rf_param_grid, n_jobs=-1, n_iter=10, cv=5)
    xgb_random_search = RandomizedSearchCV(xgb.XGBRegressor(), param_distributions=xgb_param_grid, n_jobs=-1, n_iter=10, cv=5)
    print("Done with hyperparameter optimization!")

    # create and deploy optimized model
    print("Fitting optimized models...")
    rf_random_search.fit(X_train, y_train)
    xgb_random_search.fit(X_train, y_train)
    optimized_rf_r = pd.DataFrame(rf_random_search.cv_results_)[["mean_test_score","param_max_depth","param_max_features", "param_min_samples_split", "param_min_samples_leaf", "mean_fit_time","rank_test_score",]].set_index("rank_test_score").sort_index().T
    max_depth_val_rf = int(optimized_rf_r.iloc[1,1]) if optimized_rf_r.iloc[1,1] >= 1 else float(optimized_rf_r.iloc[1,1])
    max_features_val_rf = int(optimized_rf_r.iloc[1,2]) if optimized_rf_r.iloc[1,2] >= 1 else float(optimized_rf_r.iloc[1,2])
    min_sample_split_val_rf = int(optimized_rf_r.iloc[1,3]) if optimized_rf_r.iloc[1,3] > 1 else float(optimized_rf_r.iloc[1,3])
    min_samples_leaf_val_rf = int(optimized_rf_r.iloc[1,4]) if optimized_rf_r.iloc[1,4] >= 1 else float(optimized_rf_r.iloc[1,4])

    optimized_xgb_r = pd.DataFrame(xgb_random_search.cv_results_)[["mean_test_score","param_max_depth","mean_fit_time","rank_test_score",]].set_index("rank_test_score").sort_index().T
    max_depth_val_xgb = int(optimized_xgb_r.iloc[1,1]) if optimized_xgb_r.iloc[1,1] >= 1 else float(optimized_xgb_r.iloc[1,1])
    
    rf_optimal = RandomForestRegressor(max_depth = max_depth_val_rf, max_features = max_features_val_rf, min_samples_split = min_sample_split_val_rf, min_samples_leaf = min_samples_leaf_val_rf)
    rf_optimal.fit(X_train, y_train)
    score_rf = rf_optimal.score(X_test, y_test)
    print(f"Optimized Random Forest model test score: {score_rf}")

    xgb_optimal = xgb.XGBRegressor(max_depth = max_depth_val_xgb)

    xgb_optimal.fit(X_train, y_train)
    score_xgb = xgb_optimal.score(X_test, y_test)
    print(f"Optimized XGBoost model test score: {score_xgb}")

    # obtain feature importance
    feature_names = list(X_train.columns)
    data_rf = {
        "Importance": rf_optimal.feature_importances_,
    }
    imps_rf = pd.DataFrame(data=data_rf, index=feature_names,).sort_values(by="Importance", ascending=False)[:10]
    
    data_xgb = {
        "Importance": xgb_optimal.feature_importances_,
    }
    imps_xgb = pd.DataFrame(data=data_xgb, index=feature_names,).sort_values(by="Importance", ascending=False)[:10]
    return imps_rf, imps_xgb

def number_of_atoms(atom_list, df):
    """
    Determine the number of atoms each ligand has for a given dataframe.
    
    Parameters
    ----------
    atom_list : list
        List of atom name abbreviations.
    df : dataframe
        Data containing initial data on ligand properties.

    Returns
    -------
    None
    """
    # determine the number of different heavy atoms in each ligand
    for i in atom_list:
        substruct_list = []
        for index, row in df.iterrows():
            smile_string = row['smiles']
            if len(i) == 1:
                string_finder_lower = re.findall(r'{}(?![aelu+][+\d])(?!([aeolu]+[+\d]))'.format(i.lower()), smile_string)
                string_finder_upper = re.findall(r'{}(?![aelu+][+\d])(?!([aeolu]+[+\d]))'.format(i), smile_string)
                substruct_list.append(len(string_finder_lower) + len(string_finder_upper))
            else:
                string_finder_brackets = re.findall(r'[\[]{}[\]]'.format(i), smile_string)
                string_finder_charged = re.findall(r'[\[]{}[+][+\d]'.format(i), smile_string)
                substruct_list.append(len(string_finder_brackets) + len(string_finder_charged))
        df['num_of_{}_atoms'.format(i)] = substruct_list

def atom_weights(df):
    """
    Calculate the weight of each ligand in a dataframe.
    
    Parameters
    ----------
    df : dataframe
        Dataframe of ligand properties that includes atom counts (number_of_atoms function).

    Returns
    -------
    None
    """
    # calculate weight of ligands
    global atom_weights_dict
    atom_weights_dict = {
        'C':12.0096,
        'N': 14.006,
        'O': 15.999,
        'F': 18.998,
        'Al': 26.981,
        'P': 30.974,
        'S': 32.059,
        'Cl': 35.45,
        'Cr': 51.9961,
        'Mn': 54.938,
        'Fe': 55.845,
        'Co': 58.933,
        'Ni': 58.693,
        'Cu': 63.546,
        'Zn': 65.38,
        'Ga': 69.723,
        'Ge': 72.630,
        'As': 74.921,
        'Br': 79.901,
        'Zr': 91.224,
        'Mo': 95.95,
        'Pd': 106.42,
        'Ag': 107.8682,
        'Cd': 112.414,
        'In': 114.818,
        'Sn': 118.71,
        'Sb': 121.760,
        'I': 126.904,
        'Ir': 192.217,
        'Pt': 195.08,
        'Au': 196.966570,
        'Hg': 200.592,
        'Pb': 207.2,
        'Bi': 208.980
    }
    ligand_weights = []
    for index, row in df.iterrows():
        ligand_atom_nums = sum(row[6:])
        weight_da = 0
        if int(row['num_of_heavy_atoms']) == ligand_atom_nums:
            for num, column in enumerate(row[6:]):
                column_title = list(df)[num + 6]
                atom_name = re.split("_", column_title)
                atom_type_weight = atom_weights_dict[atom_name[2]]
                weight_da = weight_da + (atom_type_weight *  column)
        weight_da = weight_da + ((row.loc['num_of_atoms'] - row.loc['num_of_heavy_atoms']) * 1.007)
        ligand_weights.append(weight_da)
    df.insert(2, "molecular_weight", ligand_weights)

def chemical_physical_properties(df, quiet = True):
    """
    Calculate various properties for each ligand in a dataframe including 
    logP (partition coefficient), hydrogen bond donors, hydrogen bond acceptors,
    molar refractivity (Ghose filter), number of rotatable bonds (Veber's rule) and polar surface
    area (Veber's rule).
    
    Parameters
    ----------
    df : dataframe
        Data containing initial data on ligand properties.

    Returns
    -------
    None
    """
    log_P = []
    H_donors = []
    H_acceptors = []
    mol_mr = []
    mol_rotatable = []
    tpsas = []
    for index, row in df.iterrows():
        mol = row.loc["mol"]
        if type(mol) != float:
            log = Crippen.MolLogP(mol)
            log_P.append(log)
            donor = Lipinski.NumHDonors(mol)
            H_donors.append(donor)
            acceptor = Lipinski.NumHAcceptors(mol)
            H_acceptors.append(acceptor)
            mr = Crippen.MolMR(mol)
            mol_mr.append(mr)
            rotatable = Lipinski.NumRotatableBonds(mol)
            mol_rotatable.append(rotatable)
            psa = Descriptors.TPSA(mol)
            tpsas.append(psa)
        else:
            if quiet == False:
                print(f"Could not calculate properties for molecule {row['filename_hydrogens']}")
            log_P.append(np.nan)
            H_donors.append(np.nan)
            H_acceptors.append(np.nan)
            mol_mr.append(np.nan)
            mol_rotatable.append(np.nan)
            tpsas.append(np.nan)
    df.insert(3, "log_P", log_P)
    df.insert(4, "H_donors", H_donors)
    df.insert(5, "H_acceptors", H_acceptors)
    df.insert(6, "mol_refractivity", mol_mr)
    df.insert(7, "rotatable_bonds", mol_rotatable)
    df.insert(8, "polar_surface_area", tpsas)

def get_ligand_properties(lig_df, quiet = True):
    """
    Determine the importance of ligand features in determining binding affinity.
    
    Parameters
    ----------
    lig_df : dataframe
        Data containing initial data on ligand properties.

    Returns
    -------
    updated_df : dataframe
        Dataframe containing calculated ligand properties of interest.
    """
    # determine and record the number of atoms and the number of heavy atoms in each ligand
    global atom_abbriv
    atom_abbriv = ['C','N','O','F','Al','P','S','Cl','Cr','Mn','Fe','Co','Ni','Cu',
               'Zn','Ga','Ge','As','Br','Zr','Mo','Pd','Ag','Cd','In','Sn','Sb',
               'I','Ir','Pt','Au','Hg','Pb','Bi']

    mol_format = []
    atom_total = []
    atom_total_heavy = []
    updated_df = lig_df.copy()
    for index, row in updated_df.iterrows():
        try:
            mol = Chem.MolFromMol2File(row['filename_hydrogens'],removeHs=False)
            if quiet == False:
                print(f"Read mol2 file for {row['filename_hydrogens']} successfully.") # TEST TEST
            if (mol is not None) and (mol is not np.nan):
                mol_format.append(mol)
                mol_atoms = mol.GetNumAtoms()
                atom_total.append(mol_atoms)
                mol_atoms_heavy = mol.GetNumHeavyAtoms()
                atom_total_heavy.append(mol_atoms_heavy)
            else:
                #currently only works for molecules containing only atoms with single letter names, need to fix
                string = row['smiles']
                string_alpha = re.findall(r'[a-zA-Z]', string)
                string_H = re.findall(r'[H]', string)
                mol_format.append(np.nan)
                atom_total.append(len(string_alpha))
                atom_total_heavy.append(len(string_alpha) - len(string_H))
        except OSError:
            if quiet == False:
                print(f"Could not read mol2 file for {row['filename_hydrogens']}, attempting to create from SMILES string...") # TEST TEST
            mol = Chem.MolFromSmiles(row['smiles'])
            if mol is not None:
                mol_H = Chem.AddHs(mol)
                mol_format.append(mol_H)
                mol_atoms = mol_H.GetNumAtoms()
                atom_total.append(mol_atoms)
                mol_atoms_heavy = mol_H.GetNumHeavyAtoms()
                atom_total_heavy.append(mol_atoms_heavy)
            else:
                #currently only works for molecules containing only atoms with single letter names, need to fix
                string = row['smiles']
                string_alpha = re.findall(r'[a-zA-Z]', string)
                string_H = re.findall(r'[H]', string)
                mol_format.append(np.nan)
                atom_total.append(len(string_alpha))
                atom_total_heavy.append(len(string_alpha) - len(string_H))
    updated_df['mol'] = mol_format
    updated_df['num_of_atoms'] = atom_total
    updated_df['num_of_heavy_atoms'] = atom_total_heavy
    number_of_atoms(atom_abbriv, updated_df)
    atom_weights(updated_df)
    chemical_physical_properties(updated_df)
    
    return updated_df
