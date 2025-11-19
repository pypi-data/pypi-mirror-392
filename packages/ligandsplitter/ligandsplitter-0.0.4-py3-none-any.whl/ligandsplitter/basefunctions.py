"""Provide the primary functions."""
import sys, os

class LigandVariables:
    """Class to hold common functional groups used in ligand analysis and derivation."""
    def __init__(self):
        #common functional groups
        self.ester = '[CX3H1,CX3](=O)[OX2H0][C;!$([C]=[O])]'
        self.ether = '[OD2]([C;!$([C]=[O])])[C;!$([C]=[O])]'
        self.hydroxy = '[OX2H;$([O]([C])[H]);!$([O](C=O)[H])][H]'
        self.carbox_acid = '[CX3;!$([CX3][H])](=O)[OX2H][H]'
        self.aldehyde = '[CX3;$(C([H])(=O)[C])](=[O;!$([O][O])])[H]'
        self.ketone = '[CX3;$(C([H])(=O)[H])](=[O;!$([O][O])])[CX3]'
        self.anhydr = 'C-[CX3](=O)[O][CX3](=O)-C'

        #nitrogen containing
        self.amine = '[C][NX3;H2;!$(NC=O)]([H])[H]'
        self.amine_2 = '[C][NX3;H;!$(NC=O)]([C])[H]'
        self.amine_3 = '[C][NX3;H0;!$(NC=O);!$(N=O)]([CX4])[CX4]'
        self.amide = '[CX3](=O)[NX3;!$(N=O)]([H])[H]' 
        self.amide_2 = '[CX3](=O)[NX3;!$(N=O)]([C])[H]'
        self.amide_3 = '[CX3](=O)[NX3;!$(N=O)]([C])[C]'
        self.nitro = 'C-N(=O)-O'
        self.imine = '[C;$(C([C,H])([C,H])=[N])]=[N][C,H]'

        #halogens
        self.f_hal = 'F'
        self.cl_hal = 'Cl'
        self.br_hal = 'Br'
        self.i_hal = 'I'

        #multiply bonded and rings
        self.alkene = 'C=C'
        self.alkyne = 'C#C'
        self.alkyne_term = 'C#C-[H]'
        self.phenyl = '[CX4;$([C][c;$(c1cc[c]cc1)]);!$([C]([H])([H])([C])[c;$(c1cc[c]cc1)])][c]1:[c]:[c]:[c]:[c]:[c]1'
        self.benzyl = '[CX4;$([C](c1ccccc1)([H])([H])[C])][c]1:[c]:[c]:[c]:[c]:[c]1'
        self.pyrrole = '[$([NH]1C=CC=C1)]'
        self.imidiz = '[$([NH]1C=NC=C1)]'
        self.pyridine = '[$([nR1]1[cR1][cR1][cR1][cR1][cR1]1)]'
        self.pyrimidine = '[$([nR1]1[cR1][nR1][cR1][cR1][cR1]1)]'

        self.type_dict = {
            'GLY': 1,
            'ALA': 1,
            'VAL': 1,
            'LEU': 1,
            'ILE': 1,
            'PRO': 1,
            'MET': 1,
            'PHE': 2,
            'TYR': 2,
            'TRP': 2,
            'SER': 3,
            'THR': 3,
            'CYS': 3,
            'ASN': 3,
            'GLN': 3,
            'ASP': 4,
            'GLU': 4,
            'ARG': 5,
            'HIS': 5,
            'LYS': 5
        }
        
        self.groups_dict = {
            'ester': ['C(=O)-[NH]-C', 'C[C](=O)[O][C](=O)C'],
            'ether': ['C-S-C'],
            'hydroxy': ['C(=O)[OH]', 'C(=O)-[H]', 'C(=O)-Cl'],
            'carbox_acid': ['C(=O)-[H]', 'C(=O)-Cl', 'C-[NH2]'],
            'aldehyde': ['C(=O)[OH]', 'C(=O)-Cl', 'C-[OH]', 'C-S-[H]', 'C(=[NH])[H]', 'C(-[NH2])[H][H]'],
            'ketone': ['C(-[NH2])[C]', 'C(=[NH])C'],
            'anhydr': ['C(=O)-[NH]-C','C(=O)OC'],
            'amine': ['CC', 'C-[N+](=O)-[O-]'],
            'amine_2': ['C(=O)(N(C)C)C'],
            'amide': ['C(=O)[OH]', 'C(=O)-[H]'],
            'amide_2': ['C(=O)OC'],
            'nitro': ['C-[NH2]'],
            'f_hal': ['Cl', 'Br', 'I'],
            'cl_hal': ['F', 'Br', 'I'],
            'br_hal': ['F', 'Cl', 'I'],
            'i_hal': ['F', 'Cl', 'Br'],
            'alkene': ['CC'],
            'alkyne': ["C=C", "CC"],
            'alkyne_term': ['C#N'], 
            'phenyl' : ['Cc1ccc([OH])cc1','Cc1ccc(OC)cc1', 'Cc1ccc(C)cc1', 'Cc1ccccc1'],
            'benzyl': ['CCc1ccc([OH])cc1','CCc1ccc(OC)cc1', 'CCc1ccc(C)cc1', 'CCc1ccccc1'],
            'pyrrole': ['[NH]1C=NC=C1'],
            'imidiz': ['[NH]1C=CC=C1'],
            'pyridine': ['n1cnccc1'],
            'pyrimidine': ['n1ccccc1']
        }
        
        self.groups_to_numbers = {
            'ester' : 1,
            'ether' : 2,
            'hydroxy' : 3,
            'carbox_acid' : 4,
            'aldehyde' : 5,
            'anhydr' : 6,
            'amine' : 7,
            'amine_2' : 8,
            'amine_3': 9,
            'amide' : 10,
            'amide_2' : 11,
            'amide_3' : 12,
            'nitro' : 13,
            'imine' : 14,
            'f_hal' : 15,
            'cl_hal' : 16,
            'br_hal' : 17,
            'i_hal' : 18,
            'alkene' : 19,
            'alkyne' : 20,
            'alkyne_term' : 21,
            'phenyl' : 22,
            'benzyl' : 23,
            'pyrrole' : 24,
            'imidiz' : 25,
            'pyridine' : 26,
            'pyrimidine' : 27
        }
    
        self.functional_groups = [self.ester, self.ether, self.hydroxy, self.carbox_acid, self.aldehyde, self.anhydr, self.amine, self.amine_2, self.amine_3, 
                        self.amide, self.amide_2, self.amide_3, self.nitro, self.imine, self.f_hal, self.cl_hal, self.br_hal, self.i_hal, self.alkene, 
                        self.alkyne, self.alkyne_term, self.phenyl, self.benzyl, self.pyrrole, self.imidiz, self.pyridine, self.pyrimidine]
        
        self.functional_groups_dict = {
            self.ester : 'ester',
            'C(=O)OC': "ester",
            self.ether : 'ether',
            self.hydroxy : 'hydroxy',
            'C-[OH]': "hydroxy",
            self.carbox_acid : 'carbox_acid',
            "C(=O)[OH]": 'carbox_acid',
            self.aldehyde :'aldehyde',
            'C(=O)-[H]': "aldehyde",
            self.anhydr : 'anhydr',
            'C[C](=O)[O][C](=O)C': "anhydr",
            self.amine : 'amine',
            "C-[NH2]": 'amine',
            'C(-[NH2])[H][H]': "amine",
            'C(-[NH2])[C]': "amine",
            self.amine_2 : 'amine_2',
            self.amine_3: 'amine_3',
            self.amide : 'amide',
            self.amide_2 : 'amide_2',
            self.amide_3: 'amide_3',
            'C(=O)(N(C)C)C': "amide_3",
            self.nitro : 'nitro',
            'C-[N+](=O)-[O-]': "nitro",
            self.imine: 'imine',
            'C(=[NH])C': "imine",
            'C(=[NH])[H]': "imine",
            self.f_hal :'f_hal',
            "F" : 'f_hal',
            self.cl_hal : 'cl_hal',
            "Cl" : 'cl_hal',
            self.br_hal : 'br_hal',
            "Br" : 'br_hal',
            self.i_hal : 'i_hal',
            "I" : 'i_hal',
            self.alkene : 'alkene',
            "CC" : 'alkene',
            self.alkyne : 'alkyne',
            self.alkyne_term : 'alkyne_term',
            self.phenyl : 'phenyl',
            self.benzyl : 'benzyl',
            self.pyrrole : 'pyrrole',
            '[NH]1C=CC=C1': "pyrrole",
            self.imidiz : 'imidiz',
            '[NH]1C=NC=C1': "imidiz",
            self.pyridine : 'pyridine',
            'n1ccccc1': "pyridine",
            self.pyrimidine : 'pyrimidine',
            'n1cnccc1': "pyrimidine",
            "C#N" :"cyanate",
            'C(=O)-Cl': "acyl chloride",
            'C-S-[H]': "thiol",
            'C-S-C': "sulfide",
            "C(=O)-[NH]-C": "carboxamide",
            "Cc1ccc([OH])cc1": "phenol",
            'CCc1ccc([OH])cc1': "benzyl alcohol",
            'Cc1ccc(C)cc1': "toluene",
            'CCc1ccc(C)cc1': "methylbenzene",
            'Cc1ccccc1': "phenyl",
            'CCc1ccccc1': "benzyl",
            'Cc1ccc(OC)cc1': "anisole",
            'CCc1ccc(OC)cc1': "benzyl methyl ether"
        }

def create_folders(dir = ""):
    """
    Create data path/dir and sub folders for each file type, return error if exists.

    Parameters
    ----------
    None

    Returns
    -------
    current_dir : String
        Current directory that is in use.
    """

    global current_dir
    if dir != "":
        current_dir = dir
    else:
        current_dir = os.getcwd()
    dataPath = os.path.join(current_dir, "data")
    try:
        os.mkdir(dataPath)
        print("Created directory:", dataPath)
    except OSError as error:
        if error.errno != 17:
            print(error)

    # create pdb file path/dir, return error if exists
    pdbPath = os.path.join(dataPath, "PDB_files")
    try:
        os.mkdir(pdbPath)
        print("Created directory:", pdbPath)
    except OSError as error:
        if error.errno != 17:
            print(error)

    # create mol2 file path/dir, return error if exists
    mol2Path = os.path.join(dataPath, "MOL2_files")
    try:
        os.mkdir(mol2Path)
        print("Created directory:", mol2Path)
    except OSError as error:
        if error.errno != 17:
            print(error)

    # create pdbqt file path/dir, return error if exists
    pdbqtPath = os.path.join(dataPath, "PDBQT_files")
    try:
        os.mkdir(pdbqtPath)
        print("Created directory:", pdbqtPath)
    except OSError as error:
        if error.errno != 17:
            print(error)

    # create test file path/dir, return error if exists
    testPath = os.path.join(dataPath, "test_files")
    try:
        os.mkdir(testPath)
        print("Created directory:", testPath)
    except OSError as error:
        if error.errno != 17:
            print(error)
    
    # create vina_out file path/dir, return error if exists
    vina_out = os.path.join(dataPath, "vina_out")
    try:
        os.mkdir(vina_out)
        print("Created directory:", vina_out)
    except OSError as error:
        if error.errno != 17:
            print(error)

    # create vina_out_2 file path/dir, return error if exists
    vina_out_2 = os.path.join(dataPath, "vina_out_2")
    try:
        os.mkdir(vina_out_2)
        print("Created directory:", vina_out_2)
    except OSError as error:
        if error.errno != 17:
            print(error)

    # create smina_out file path/dir, return error if exists
    smina_out = os.path.join(dataPath, "smina_out")
    try:
        os.mkdir(smina_out)
        print("Created directory:", smina_out)
    except OSError as error:
        if error.errno != 17:
            print(error)

    # create smina_out_2 file path/dir, return error if exists
    smina_out_2 = os.path.join(dataPath, "smina_out_2")
    try:
        os.mkdir(smina_out_2)
        print("Created directory:", smina_out_2)
    except OSError as error:
        if error.errno != 17:
            print(error)
    
    return current_dir

def convert_type(start_type):
    """
    Determine if the start_type is a string or an integer.
    Used in ligand splitting to determine what information is in a given line of a MOL2 file.

    Parameters
    ----------
    start_type : String or int

    Returns
    -------
    bool
        If the start_type is a string, bool is False; if an integer, bool is True.
    """

    try:
        isinstance(int(start_type), int)  
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    # Do something if this file is invoked on its own
    create_folders()
