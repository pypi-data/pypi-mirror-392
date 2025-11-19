"""Functions used to validate ligand structure and remove redundant ligands."""
from rdkit import Chem
from rdkit import RDLogger

def parse_unique_ligands(smiles_list, ligs):
    """
    Determine unique ligands from a list of SMILES strings.

    Parameters
    ----------
    smiles_list : list
        List of SMILES strings representing ligands.
    ligs : list
        List of ligand identifiers.

    Returns
    -------
    ligs : list
        List of unique ligand identifiers.
    filenames : list
        List of filenames corresponding to the unique ligands.
    """

    new_ligs = []
    new_filenames = []
    exclude_ligs = []
    mol_total = len(smiles_list)
    for h, i in enumerate(smiles_list):
        print(f"Testing ligand number {str(h + 1)}...")
        mol_number = int(h + 1)
        while mol_number < mol_total:
            if (i == smiles_list[mol_number]) and (ligs[mol_number] not in exclude_ligs):
                exclude_ligs.append(ligs[mol_number])
            mol_number += 1
    for ligand in ligs:
        if exclude_ligs.count(ligand) == 0:
            new_ligs.append(ligand)
            new_filenames.append("data/MOL2_files/" + str(ligand) + ".mol2")
    ligs = new_ligs
    filenames = new_filenames
    print(f"Done! List of ligands with unique structures: {ligs}")
    return ligs, filenames

def validate_unique_ligands(ligs):
    """
    Ensure that ligands follow the correct format and do not violate atomic properties (e.g. number of bonds per atom) and are unique.

    Parameters
    ----------
    ligs : list
        List of ligand identifiers.

    Returns
    -------
    ligs : list
        List of unique ligand identifiers.
    filenames : list
        List of filenames corresponding to the unique ligands.
    """
    
    RDLogger.DisableLog('rdApp.*') 
    mol_list = []
    smiles_list = []
    ligs = list(set(ligs))
    for i in ligs:
        file = "data/MOL2_files/" + str(i) + ".mol2"
        mol = Chem.MolFromMol2File(file, sanitize=False)
        if mol is not None:
            select_mol_smile = Chem.MolToSmiles(mol)
            smiles_list.append(select_mol_smile)
            mol_list.append(mol)
    ligs, filenames = parse_unique_ligands(smiles_list, ligs)
    return ligs, filenames
