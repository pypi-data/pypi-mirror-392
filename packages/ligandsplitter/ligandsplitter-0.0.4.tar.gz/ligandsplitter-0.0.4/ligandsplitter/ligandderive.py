"""Provide the primary functions."""
import sys, os
import numpy as np
import re
from rdkit import Chem
from rdkit.Chem import AllChem
from openbabel import pybel
from .basefunctions import LigandVariables

vars = LigandVariables()

def get_func_groups(ligs):
    """
    Get functional groups for each ligand.
    
    Parameters
    ----------
    ligs : list
        List of ligand names.

    Returns
    -------
    all_func_groups : list
        List of functional groups for each ligand (1 if present for a given ligand, 0 if absent).
    all_derivs_mols : list
        RDKit Mol objects for each derivative.
    all_derivs_smiles : list
        SMILES strings for each derivative.
    deriv_created : dict
        Descriptions of each derivative created (each value is a list containing the name of the original ligand and the functional group that was replaced).
    """
    all_func_groups = []
    all_derivs_mols = []
    all_derivs_smiles = []
    deriv_created = {}
    for i in ligs:
        mol_groups = []
        try:
            mol = Chem.MolFromMol2File(f"data/MOL2_files/{i}_H.mol2", sanitize = False)
        except:
            mol_proto = [m for m in pybel.readfile(filename= f"data/MOL2_files/{i}.mol2",format='mol2')][0]
            mol_proto.addh()
            out = pybel.Outputfile(filename= "data/MOL2_files/" + str(i) + "_H.mol2",format='mol2',overwrite=True)
            out.write(mol_proto)
            out.close()
            mol = Chem.MolFromMol2File(f"data/MOL2_files/{i}_H.mol2", sanitize = False)
        mol_neworder = tuple(zip(*sorted([(j, i) for i, j in enumerate(Chem.CanonicalRankAtoms(mol))])))[1]
        mol_renum = Chem.RenumberAtoms(mol, mol_neworder)
        for j in vars.functional_groups:
            k = Chem.MolFromSmarts(j)
            if mol_renum.HasSubstructMatch(k):
                mol_groups.append(1) # 1 corresponds to a functional group being present
                derivs, deriv_smiles, deriv_type = derive(i, j)
                all_derivs_mols.extend(derivs)
                all_derivs_smiles.extend(deriv_smiles)
                deriv_created.update(deriv_type)
            else:
                mol_groups.append(0) # 0 corresponds to a functional group being absent
        all_func_groups.append(mol_groups)
    return all_func_groups, all_derivs_mols, all_derivs_smiles, deriv_created

def derive(ligand, group):
    """
    Create derivative ligands from a given ligand.
    
    Parameters
    ----------
    ligand : string
        Ligand name.
    group : string
        SMILES representation of the functional group to be replaced.

    Returns
    -------
    derivative_mols : list
       RDKit Mol objects for each derivative.
    derivative_smile : list
        SMILES strings for each derivative.
    deriv_type : dict
         Descriptions of each derivative created (each value is a list containing the name of the original ligand and the functional group that was replaced).
    """
    derivative_mols = []
    derivative_smile = []
    deriv_type = {}

    mol = Chem.MolFromMol2File(f"data/MOL2_files/{ligand}_H.mol2", sanitize = False)
    old_substr = Chem.MolFromSmarts(group)
    if vars.functional_groups_dict[group] in vars.groups_dict:
        replacement_values = vars.groups_dict[vars.functional_groups_dict[group]]
        for a in replacement_values:
            if a != group:
                new_substr = Chem.MolFromSmiles(a)
                rms = AllChem.ReplaceSubstructs(mol, old_substr, new_substr)
                fragments = Chem.GetMolFrags(rms[0])
                for frag in fragments:
                    ind_frag = Chem.MolFragmentToSmiles(rms[0], frag)
                    if (len(ind_frag) > 25) & (ind_frag != "O[H][H]") & (ind_frag not in derivative_smile):
                        derivative_smile.append(ind_frag)
                        new_functional_group = vars.functional_groups_dict[a]
                        deriv_type[ind_frag] = [vars.functional_groups_dict[group], new_functional_group, ligand]
                        temp_mol = Chem.MolFromSmiles(ind_frag)
                        if temp_mol is not None:
                            derivative_mols.append(temp_mol)
                        else:
                            print(f"Could not create RDKit mol object from SMILES {ind_frag}")
                            derivative_mols.append(None)
    return derivative_mols, derivative_smile, deriv_type

def create_derivative_files(all_derivs_mols, all_derivs_smiles, deriv_created):
    """
    Create derivative ligands from a given ligand.
    
    Parameters
    ----------
    all_derivs_mols : list
        List of RDKit Mol objects for each derivative.
    all_derivs_smiles : list
        SMILES strings for each derivative.
    deriv_created : dict
        Descriptions of each derivative created.

    Returns
    -------
    derivs : list
       List containing names for each created derivative.
    fxnal_groups_derivs : list
        List of functional groups contained in each derivative (1 if present for a given derivative, 0 if absent).
    """
    derivs = []
    fxnal_groups_derivs = []
    for mol_num, mol in enumerate(all_derivs_mols):
        if mol is not None:
            descriptor = deriv_created[all_derivs_smiles[mol_num]]
            new_ligand = 'derivative_' + str(descriptor[0]) + '_' + str(descriptor[1])
            iter_var = 0
            while new_ligand in derivs:
                iter_var += 1
                new_ligand = 'derivative_' + str(descriptor[0]) + '_' + str(descriptor[1] + '_' + str(iter_var))
            pdb_file = 'data/PDB_files/' + str(new_ligand) + '.pdb'
            Chem.MolToPDBFile(mol, pdb_file)
    
            # make mol2 file
            pdb_mol = [m for m in pybel.readfile(filename = pdb_file, format='pdb')][0]
            out = pybel.Outputfile(filename= f"data/MOL2_files/{new_ligand}.mol2", overwrite = True, format='mol2')
            out.write(pdb_mol)
            out.close()
    
            # make mol2 file (including hydrogens)
            mol2_mol = [m for m in pybel.readfile(filename = f"data/MOL2_files/{new_ligand}.mol2", format='mol2')][0]
            mol2_mol.make3D()
            mol2_mol.addh()
            out = pybel.Outputfile(filename= f"data/MOL2_files/{new_ligand}_H.mol2", overwrite = True, format='mol2')
            out.write(mol2_mol)
            out.close()
    
            # make pdbqt file
            out2 = pybel.Outputfile(filename= f"data/PDBQT_files/{new_ligand}.pdbqt", overwrite = True, format='pdbqt')
            out2.write(mol2_mol)
            out2.close()

            # get functional groups of derivatives
            mol_groups = []
            for j in vars.functional_groups:
                k = Chem.MolFromSmarts(j)
                if mol.HasSubstructMatch(k):
                    mol_groups.append(1) # 1 corresponds to a functional group being present
                else:
                    mol_groups.append(0) # 0 corresponds to a functional group being absent
            fxnal_groups_derivs.append(mol_groups)
            derivs.append(new_ligand)
    return derivs, fxnal_groups_derivs