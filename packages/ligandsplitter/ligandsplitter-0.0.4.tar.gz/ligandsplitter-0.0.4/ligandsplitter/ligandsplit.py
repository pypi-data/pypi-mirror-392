"""Functions used to retrieve and split ligands from a PDB ID."""
import numpy as np
import re
import sys, os
from Bio.PDB import PDBList, PDBIO
from Bio.PDB.MMCIFParser import MMCIFParser
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
import MDAnalysis as mda 
from openbabel import pybel
from .basefunctions import convert_type

class File_Info:
    def __init__(self, tripos_mol, tripos_atom, tripos_bond, lines_mols, lines_atoms, lines_bonds):
        self.tripos_mol = tripos_mol
        self.tripos_atom = tripos_atom
        self.tripos_bond = tripos_bond
        self.lines_mols = lines_mols
        self.lines_atoms = lines_atoms
        self.lines_bonds = lines_bonds

class Ligand:
    def __init__(self, name, lines_mol, lines_atom, lines_bond):
        self.name = name
        self.lines_mol = lines_mol
        self.lines_atom = lines_atom
        self.lines_bond = lines_bond
    @property
    def lines_mol(self):
        return self._lines_mol

    @property
    def lines_atom(self):
        return self._lines_atom
    
    @property
    def lines_bond(self):
        return self._lines_bond
    
    @lines_mol.setter
    def lines_mol(self, lines_mol):
        self._lines_mol = lines_mol
        self.mol_header = lines_mol[0]
        self.mol_name = lines_mol[1]
        self.mol_info = lines_mol[2]
        self.mol_type = lines_mol[3]
        self.charge_type = lines_mol[4]
        
    @lines_atom.setter
    def lines_atom(self, lines_atom):
        self._lines_atom = lines_atom
        self.num_atoms = lines_atom[-1] - lines_atom[0] + 1
        
    @lines_bond.setter
    def lines_bond(self, lines_bond):
        self._lines_bond = lines_bond
        self.num_bonds = lines_bond[-1] - lines_bond[0] + 1

def retrieve_pdb_file(pdb_id, format = ""):
    """
    Retrieve PDB/MMCIF file from RCSB database and isolate macromolecule from ligands/ions.

    Parameters
    ----------
    pdb_id : String
        Set to PDB ID of interest or to file name if local file
    format: String (pdb, mmcif, or local)

    Returns
    -------
    None
    """

    # isolate protein
    pdb_list = PDBList()
    global pdb_filename
    atom_lines_added = 0
    clean_ligand_exists = True
    # List of residue names for elemental ions
    list_of_ions = ["AG", "AL", "AM", "AU", "AU3", "BA", "BR", "BS3", "CA", "CD", "CE", "CF", "CL", "CO", "3CO", "CR", 
                    "CS", "CU1", "CU", "CU3", "DY", "ER3", "EU3", "EU", "F", "FE", "FE2", "GA", "GD3", "HG", "IN", 'IOD', 
                    "IR3", "IR", "K", "LA", "LI", "LU", "MG", "MN", "MN3", "4MO", "6MO", "NA", "ND", "NI", "3NI", "OS", 
                    "OS4", "PB", "PD", "PR", "PT", "PT4", "4PU", "RB", "RH3", "RHF", "RU", "SB", "SM", "SR", "TB", "TH", 
                    "4TI", "TL", "V", "W", "Y1", "YB", "YB2", "YT3", "ZCM", "ZN", "ZR", "ZTM"]
    # List of amino acid residue names
    res_list = ["ALA", "CYS", 'ASP', 'GLU','PHE','GLY', 'HIS', 'ILE', 'LYS', 'LEU', 'MET', 'ASN', 'PRO', 'GLN', 'ARG', 'SER', 'THR', 'VAL', 'TRP', 'TYR']
    if format == "pdb":
        covalent_ligs = []
        pdb_filename = pdb_list.retrieve_pdb_file(pdb_id, pdir="data/PDB_files", file_format="pdb")
        with open(pdb_filename,"r") as outfile:
            data = outfile.readlines()
            for line in data:
                # check to see if any ligands are covalently bound to protein
                # if present, record the id, chain number, and residue number
                if 'LINK' in line:
                    split_line = line.split()
                    if (split_line[2] in res_list) and (split_line[6] not in covalent_ligs) and (split_line[6] not in res_list) and (split_line[6] != "HOH"):
                        covalent_ligs.append(split_line[6])
                    elif (split_line[6] in res_list) and (split_line[2] not in covalent_ligs) and (split_line[2] not in res_list) and (split_line[2] != "HOH"):
                        covalent_ligs.append(split_line[2])
        u = mda.Universe(pdb_filename)
        selection = "protein"
        selection_ligand = "not protein and not resname HOH"
        for lig in covalent_ligs:
            selection = selection + " or resname " + lig
            selection_ligand = selection_ligand + " and not resname " + lig
        protein = u.select_atoms(selection)
        protein.write(f"data/PDB_files/{pdb_id}_protein.pdb")
    
        # isolate ligands and remove water molecules from PDB file
        ligand = u.select_atoms(selection_ligand)
        try:
            ligand.write(f"data/PDB_files/{pdb_id}_ligand.pdb")
        except IndexError:
            print(f"Macromolecule from PDB ID {pdb_id} has no ligands present. PDB file of macromolecule has been saved to data/PDB_files/{short_filename}_protein.pdb")
        try:
            with open(f"data/PDB_files/{pdb_id}_clean_ligand.pdb", 'w+') as datafile: 
                with open(f"data/PDB_files/{pdb_id}_ligand.pdb","r") as outfile:
                    data = outfile.readlines()
                for line in data:
                    if 'HETATM' in line:
                        split_line = line.split()
                        line_1_join = split_line[1] # residue number
                        line_2_join = split_line[2] # atom name
                        line_3_join = split_line[3] # residue name
                        if 'HETATM' not in split_line[0]:
                            datafile.write(line)
                        # only write hetatm lines if they are not atomic ions -- if the alphabetical characters in the
                        # res name column and atom name column are the same, it is likely an atomic ion. compare res name
                        # to entries in list_of_ions
                        elif (split_line[0] == 'HETATM') and (line_2_join != line_3_join) and (line_3_join not in list_of_ions):
                            datafile.write(line)
                            atom_lines_added += 1
                        # if res number is 10000 or greater, columns for atom type and res number are counted as one
                        # due to lack of white space, affecting numbering. compare res name to entries in list_of_ions
                        elif (split_line[0] != 'HETATM') and (line_1_join != line_2_join)and (line_2_join not in list_of_ions):
                            datafile.write(line)
                            atom_lines_added += 1
                    else:
                        datafile.write(line)
        except FileNotFoundError:
            clean_ligand_exists = False
    elif format == "mmcif":
        pdb_filename = pdb_list.retrieve_pdb_file(pdb_id, pdir="data/PDB_files", file_format="mmCif")
        # parse mmcif file and produce a pdb file with only the receptor present
        covalent_ligs = []
        p = MMCIFParser()
        mmcifdict = MMCIF2Dict(pdb_filename)
        nonstandard_res = list(mmcifdict["_entity_poly.nstd_monomer"])
        nonstandard_code = list(mmcifdict["_entity_poly.pdbx_seq_one_letter_code"])
        struc_prot = p.get_structure("", pdb_filename)
        for model in struc_prot:
            for chain_num, chain in enumerate(model):
                # remove non-protein residues unless they are covalently bound ligands
                one_letter_code = nonstandard_code[chain_num]
                x = re.findall(r"\((.*?)\)", one_letter_code)
                for res in x:
                    covalent_ligs.append(f"H_{res}")
                for residue in list(chain):
                    residue.get_resname()
                    res_id = residue.id
                    if (res_id[0] != ' ') and (nonstandard_res[chain_num] == "no"):
                        chain.detach_child(res_id)
                    elif nonstandard_res[chain_num] == "yes":
                        if (res_id[0] != ' ') and (res_id[0] not in covalent_ligs):
                            chain.detach_child(res_id)
        io = PDBIO()
        io.set_structure(struc_prot)
        io.save(f"data/PDB_files/{pdb_id}_protein.pdb")
        # get ligand information from mmcif file if available
        p = MMCIFParser()
        struc_lig = p.get_structure("", pdb_filename)
        for model in struc_lig:
            for chain in model:
                for residue in list(chain):
                    res_id = residue.id
                    if res_id[0] == ' ' or res_id[0] == 'W':
                        chain.detach_child(res_id)
                    else:
                        if res_id[0] in covalent_ligs:
                            chain.detach_child(res_id)
                        for value in list_of_ions:
                            if res_id[0] == f'H_{value}':
                                chain.detach_child(res_id)
        io = PDBIO()
        io.set_structure(struc_lig)
        io.save(f"data/PDB_files/{pdb_id}_clean_ligand.pdb")
        with open(f"data/PDB_files/{pdb_id}_clean_ligand.pdb","r") as outfile:
            data = outfile.readlines()
            for line in data:
                if 'HETATM' in line:
                    atom_lines_added += 1
        if atom_lines_added == 0:
            clean_ligand_exists = False
    elif format == "local":
        format_subset = pdb_id.split(".")[-1]
        remainder = pdb_id.split(".")[0]
        short_filename = remainder.split("/")[-1]
        if ("pdb" in format_subset) or ("ent" in format_subset):
            covalent_ligs = []
            with open(pdb_id, "r") as outfile:
                data = outfile.readlines()
                for line in data:
                    # check to see if any ligands are covalently bound to protein
                    # if present, record the id, chain number, and residue number
                    if 'LINK' in line:
                        split_line = line.split()
                        if (split_line[2] in res_list) and (split_line[6] not in covalent_ligs) and (split_line[6] not in res_list) and (split_line[6] != "HOH"):
                            covalent_ligs.append(split_line[6])
                        elif (split_line[6] in res_list) and (split_line[2] not in covalent_ligs) and (split_line[2] not in res_list) and (split_line[2] != "HOH"):
                            covalent_ligs.append(split_line[2])
            u = mda.Universe(pdb_id)
            selection = "protein"
            selection_ligand = "not protein and not resname HOH"
            for lig in covalent_ligs:
                selection = selection + " or resname " + lig
                selection_ligand = selection_ligand + " and not resname " + lig
            protein = u.select_atoms(selection)
            pdb_id = short_filename
            protein.write(f"data/PDB_files/{pdb_id}_protein.pdb")
    
            # isolate ligands and remove water molecules from PDB file
            ligand = u.select_atoms(selection_ligand)
            try:
                ligand.write(f"data/PDB_files/{pdb_id}_ligand.pdb")
            except IndexError:
                print(f"Macromolecule {pdb_id} has no ligands present. PDB file of macromolecule has been saved to data/PDB_files/{pdb_id}_protein.pdb")
            try:
                with open(f"data/PDB_files/{pdb_id}_clean_ligand.pdb", 'w+') as datafile: 
                    with open(f"data/PDB_files/{pdb_id}_ligand.pdb","r") as outfile:
                        data = outfile.readlines()
                    for line in data:
                        if 'HETATM' in line:
                            split_line = line.split()
                            line_1_join = split_line[1]
                            line_2_join = split_line[2]
                            line_3_join = split_line[3]
                            if 'HETATM' not in split_line[0]:
                                datafile.write(line)
                            # only write hetatm lines if they are not atomic ions -- if the alphabetical characters in the
                            # res name column and atom name column are the same, it is likely an atomic ion. compare res name
                            # to entries in list_of_ions
                            elif (split_line[0] == 'HETATM') and (line_2_join != line_3_join) and (line_3_join not in list_of_ions):
                                datafile.write(line)
                                atom_lines_added += 1
                            # if res number is 10000 or greater, columns for atom type and res number are counted as one
                            # due to lack of white space, affecting numbering. compare res name to entries in list_of_ions
                            elif (split_line[0] != 'HETATM') and (line_1_join != line_2_join)and (line_2_join not in list_of_ions):
                                datafile.write(line)
                                atom_lines_added += 1
                        else:
                            datafile.write(line)
            except FileNotFoundError:
                clean_ligand_exists = False
        elif "cif" in format_subset:
            # parse mmcif file and produce a pdb file with only the protein present
            covalent_ligs = []
            p = MMCIFParser()
            mmcifdict = MMCIF2Dict(pdb_id)
            nonstandard_res = list(mmcifdict["_entity_poly.nstd_monomer"])
            nonstandard_code = list(mmcifdict["_entity_poly.pdbx_seq_one_letter_code"])
            struc_prot = p.get_structure("", pdb_id)
            for model in struc_prot:
                for chain_num, chain in enumerate(model):
                    # remove non-protein residues unless they are covalently bound ligands
                    one_letter_code = nonstandard_code[chain_num]
                    x = re.findall(r"\((.*?)\)", one_letter_code)
                    for res in x:
                        covalent_ligs.append(f"H_{res}")
                    for residue in list(chain):
                        residue.get_resname()
                        res_id = residue.id
                        if (res_id[0] != ' ') and (nonstandard_res[chain_num] == "no"):
                            chain.detach_child(res_id)
                        elif nonstandard_res[chain_num] == "yes":
                            if (res_id[0] != ' ') and (res_id[0] not in covalent_ligs):
                                chain.detach_child(res_id)
            io = PDBIO()
            io.set_structure(struc_prot)
            io.save(f"data/PDB_files/{short_filename}_protein.pdb")
            # get ligand information from mmcif file if available
            p = MMCIFParser()
            struc_lig = p.get_structure("", pdb_id)
            for model in struc_lig:
                for chain in model:
                    for residue in list(chain):
                        res_id = residue.id
                        if res_id[0] == ' ' or res_id[0] == 'W':
                            chain.detach_child(res_id)
                        else:
                            if res_id[0] in covalent_ligs:
                                chain.detach_child(res_id)
                            for value in list_of_ions:
                                if res_id[0] == f'H_{value}':
                                    chain.detach_child(res_id)
            io = PDBIO()
            io.set_structure(struc_lig)
            pdb_id = short_filename
            io.save(f"data/PDB_files/{pdb_id}_clean_ligand.pdb")
            with open(f"data/PDB_files/{pdb_id}_clean_ligand.pdb","r") as outfile:
                data = outfile.readlines()
                for line in data:
                    if 'HETATM' in line:
                        atom_lines_added += 1
            if atom_lines_added == 0:
                clean_ligand_exists = False
        else:
            print("Unable to upload local file. Please ensure the file is in either pdb or mmcif format.")
            clean_ligand_exists = False
    else:
        clean_ligand_exists = False
        print("Invalid format entered. Please enter format as either pdb or mmcif, or as local to upload a local pdb or mmcif file.")
    # convert ligand pdb file to mol2 file, or return a warning if only elemental ions are present
    if atom_lines_added == 0 and clean_ligand_exists:
        print(f"Warning: Ligands cannot be extracted from PDB ID {pdb_id} as only atomic ions are present. PDB file of macromolecule has been saved to data/PDB_files/{pdb_id}_protein.pdb")
    elif clean_ligand_exists:
        if format == "local":
            pdb_mol2 = [m for m in pybel.readfile(filename = f"data/PDB_files/{short_filename}_clean_ligand.pdb", format='pdb')][0]
            out_mol2 = pybel.Outputfile(filename = f"data/MOL2_files/{short_filename}_ligand.mol2", overwrite = True, format='mol2')
            out_mol2.write(pdb_mol2)
            print(f"Comprehensive ligand MOL2 file extracted from {short_filename} has been saved to data/MOL2_files/{short_filename}_ligand.mol2")
        else:
            pdb_mol2 = [m for m in pybel.readfile(filename = f"data/PDB_files/{pdb_id}_clean_ligand.pdb", format='pdb')][0]
            out_mol2 = pybel.Outputfile(filename = f"data/MOL2_files/{pdb_id}_ligand.mol2", overwrite = True, format='mol2')
            out_mol2.write(pdb_mol2)
            print(f"Comprehensive ligand MOL2 file extracted from PDB ID {pdb_id} has been saved to data/MOL2_files/{pdb_id}_ligand.mol2")
    print("Download completed.")

def isolate_by_method(method, file_format, name = "", upload = {}):
    """
    Isolate protein and ligand files based on the method of retrieval (manual entry, upload, or random PDB ID).

    Parameters
    ----------
    method : String
        Name of method used to isolate receptor from ligands (Manual text entry, Upload from local file, Advanced Search, or Random).
    file_format : String
        Name of file format to be used (pdb or mmcif) or "local" if uploading a local file.
    name : String
        Name of PDB ID or file name.
    upload : tuple(dict)
        Dictionary containing the name of the uploaded file and its content.

    Returns
    -------
    protein_filename : String
        Name of the protein file.
    ligand_filename_initial : String
        Name of the ligand file.
    """

    # get PDB or MMCIF file from pdb.org using pdb id
    pdb_id = ''
    if (method == "Manual text entry") or (method == "Advanced Search") or (method == "Random"):
        pdb_id = name.lower()
        retrieve_pdb_file(pdb_id, file_format)
        protein_filename = f"data/PDB_files/{pdb_id}_protein.pdb"
        ligand_filename_initial = f"data/MOL2_files/{pdb_id}_ligand.mol2"
    
    # get PDB or MMCIF file from local upload   
    elif method == "Upload from local file":
        # get information for uploaded file
        prot_file = upload[0]['name']
        # write the uploaded file to the local directory
        with open("data/PDB_files/" + str(prot_file), "wb") as fp:
            fp.write(upload[0]["content"])
        # clean local protein file
        proto_protein_filename = "data/PDB_files/" + str(prot_file)
        short_proto_name = proto_protein_filename.split("/")[-1]
        pdb_id = short_proto_name.split(".")[0]
        # retrieve PDB file from local upload
        retrieve_pdb_file(proto_protein_filename, "local")
        protein_filename = f"data/PDB_files/{pdb_id}_protein.pdb"
        ligand_filename_initial = f"data/MOL2_files/{pdb_id}_ligand.mol2"
    else:
        print("Invalid method selected. Please select a valid method to retrieve the protein and ligand filenames.")
    return protein_filename, ligand_filename_initial

def get_mol2_info(ligand_file):
    """
    Get MOL2 file information from a ligand file to create a File_Info object.

    Parameters
    ----------
    ligand_file : String
        Name of MOL2 containing ligand information.

    Returns
    -------
    File_Info object
    """

    tripos_mol = []
    tripos_atom = []
    tripos_bond = []
    lines_mols = []
    lines_atoms = []
    lines_bonds = []
    with open(ligand_file, "r") as outfile:
        data = outfile.readlines()
        for linenum, line in enumerate(data):
            if "@<TRIPOS>MOLECULE" in line:
                tripos_mol.append(linenum)
            if "@<TRIPOS>ATOM" in line:
                tripos_atom.append(linenum)
            if '@<TRIPOS>BOND' in line:
                tripos_bond.append(linenum)
    with open(ligand_file, "r+") as outfile:
        data = outfile.readlines()
        a = 1
        # get lines corresponding to molecule information
        for instance, value in enumerate(tripos_mol):
            for linenum, line in enumerate(data):
                for i in range((linenum >= value) and (linenum < value + 5)):
                    lines_mols.append(line)
        #get lines corresponding to atom information
        for instance, value in enumerate(tripos_atom):
            for linenum, line in enumerate(data):
                for i in range((linenum > value) and (linenum < tripos_bond[instance])):
                    if (convert_type(line.split()[0])) and (len(line.split()) > 7):
                        lines_atoms.append(line)
        # get lines corresponding to bond information
        for instance, value in enumerate(tripos_bond):
            temp_bonds = []
            if len(tripos_atom) > (instance + 1):
                for linenum, line in enumerate(data):
                    for i in range((linenum > value) and (linenum < tripos_atom[instance + 1])):
                        try:
                            if (convert_type(line.split()[0])) and (len(line.split()) == 4):
                                temp_bonds.append(line)
                        except:
                            pass
                            
            else:
                for linenum, line in enumerate(data):
                    for i in range(linenum > value):
                        try:
                            if (convert_type(line.split()[0])) and (len(line.split()) == 4):
                                temp_bonds.append(line)
                        except:
                            pass
            # sort temp_bonds by atom numbers
            temp_bonds.sort(key=lambda x: int(x.split()[1]))
            for num, line in enumerate(temp_bonds):
                temp_bond_split = re.split(r"(\s+)", line)
                temp_bond_split[2] = str(num + 1)
                bond_renumbered = ''.join(str(x) for x in temp_bond_split)
                lines_bonds.append(bond_renumbered)
    return File_Info(tripos_mol, tripos_atom, tripos_bond, lines_mols, lines_atoms, lines_bonds)

def get_ligands(file_info, name_vals = {}):
    """
    Get ligand information from a File_Info object and create a list of all ligands present.

    Parameters
    ----------
    file_info : File_Info object
        Set to PDB ID of interest
    name_vals : dict
        If being used to split a mol2 file generated from SMILES strings, this dict will
        be used to rename the ligands.

    Returns
    -------
    ligand_list : list
        List of all ligands in File_Info object
    """

    ligs_temp = []
    lig_loc = []
    atoms = []
    UNL1_count = 0
    # get ligand names and atom locations for each ligand
    for linenum, line in enumerate(file_info.lines_atoms):
        ligand = line
        lig_atom = ligand.split()
        lig1 = str(lig_atom[-2])
        # if the name_vals dictionary exists, use it to name ligands
        if (len(name_vals) > 0):
            keys = list(name_vals.values())
            lig1 = keys[UNL1_count]
        # if a ligand is not in the list of identified ligands and is not labeled as 
        # "UNL1", record the line number
        if (lig1 not in ligs_temp) & (lig1 != 'UNL1') & (len(name_vals) == 0):
            ligs_temp.append(lig1)
            lig_loc.append(int(linenum))
            
        # if the number corresponding to the order of atoms is equal to one, it means
        # these atoms belong to a new ligand, record the line number
        elif (int(lig_atom[0]) == 1):
            if (len(name_vals) > 0) & (len(ligs_temp) > 0):
                UNL1_count += 1
                lig1 = keys[UNL1_count]
            ligs_temp.append(lig1)
            lig_loc.append(int(linenum))
            
        # if a ligand is in the list of identified ligands and is a different ligand 
        # than the one in the line above it, the new ligand is a duplicate of a previously
        # identified ligand, record the line number
        elif ((lig1 in ligs_temp) and (lig1 != ligs_temp[-1])):
            ligs_temp.append(lig1)
            lig_loc.append(int(linenum))
            
    lig_loc.append(len(file_info.lines_atoms))
    # get list containing the number of atoms present in each ligand
    d = 0
    while d < (len(lig_loc) - 1):
        atoms_1 = lig_loc[d + 1] - lig_loc[d]
        atoms.append(int(atoms_1))
        d += 1
    
    # get bond locations for each ligand
    lig_loc_bond = [] # bond locations/indexes for each ligand
    lig_loc_bond.append(0) # first ligand starts at line 0
    all_bonds = [] # list of all bonds in the file (contains numbers for atoms bonded to each other)
    temp_ligand_number = 0 # current ligand being processed

    #print(f"atom list: {atoms}") #TEST TEST

    for linenum, line in enumerate(file_info.lines_bonds): 
        ligand = line

        #print(f"Processing line {linenum}: {ligand}") #TEST TEST

        bond_num = ligand.split()
        atom_cap = atoms[temp_ligand_number]
        atom_sum = sum(atoms[:temp_ligand_number]) # sum of atoms in previous ligands
        bond_atom1 = int(bond_num[1])
        bond_atom2 = int(bond_num[2])
        if (len(all_bonds) > 0):
            #print(f"Current bond: {bond_atom1} - {bond_atom2}, Atom cap: {atom_cap}, Temp ligand number: {temp_ligand_number}, Last atom location: {all_bonds[-1][0]} - {all_bonds[-1][1]}") #TEST TEST
            
            # if the current atom number is reset to one or if the numbers for the atoms in the bond are greater than or equal to the sum of atoms in current ligands,
            # increment ligand number and record the line number
            if ((bond_atom1 == 1 and all_bonds[-1][0] > 1)):
                temp_ligand_number += 1
                atom_cap = atoms[temp_ligand_number]
                atom_sum = sum(atoms[:temp_ligand_number])
                lig_loc_bond.append(linenum)
        all_bonds.append([bond_atom1, bond_atom2])
        # if the ligand number is greater than 0 and if the numbers for the atoms in the bond are less than or equal to the sum of atoms in previous ligands,
        # subtract the number of atoms in previous ligands to the atom numbers in the bond line to account for the offset in numbering
        if (temp_ligand_number > 0 and (max(bond_atom1, bond_atom2) > atom_cap)):
            bond_atom1 = bond_atom1 - atom_sum
            bond_atom2 = bond_atom2 - atom_sum
        if(max(bond_atom1, bond_atom2) > atom_cap):
            temp_ligand_number += 1
            atom_cap = atoms[temp_ligand_number]
            atom_sum = sum(atoms[:temp_ligand_number])
            lig_loc_bond.append(linenum)
    lig_loc_bond.append(len(file_info.lines_bonds)) # last ligand ends at the last line of the file
    
    #print(f"atom ligand locations: {lig_loc}") #TEST TEST
    #print(f"bond ligand locations: {lig_loc_bond}") #TEST TEST

    # create Ligand instances for each ligand
    ligand_list = []
    for ligand_number, ligand in enumerate(ligs_temp):
        # get molecule info for each ligand
        # molecule info for each ligand consists of five lines: tripos header, ligand name, ligand info (atom count, bond count, etc), molecule type, and charge type
        try:
            mol_info = [file_info.lines_mols[ligand_number], file_info.lines_mols[ligand_number + 1], file_info.lines_mols[ligand_number + 2], file_info.lines_mols[ligand_number + 3], file_info.lines_mols[ligand_number + 4]]
        except IndexError:
            mol_info = [file_info.lines_mols[0], file_info.lines_mols[1], file_info.lines_mols[2], file_info.lines_mols[3], file_info.lines_mols[4]]
        # get atom info for each ligand
        ligand_atom1 = lig_loc[ligand_number]
        ligand_atom2 = lig_loc[ligand_number + 1] - 1
        atoms_for_ligand = [ligand_atom1, ligand_atom2]
        # get bond info for each ligand
        ligand_bond1 = lig_loc_bond[ligand_number]
        ligand_bond2 = lig_loc_bond[ligand_number + 1] - 1
        bonds_for_ligand = [ligand_bond1, ligand_bond2]
        # create ligand instance with relevant information and add to list of ligands
        new_lig = Ligand(name = ligand, lines_mol = mol_info, lines_atom = atoms_for_ligand, lines_bond = bonds_for_ligand)
        ligand_list.append(new_lig)
    return ligand_list

def find_ligands_unique(ligand_list):
    """
    Find all unique ligands in a list of ligands.

    Parameters
    ----------
    ligand_list : list
        List of ligands.

    Returns
    -------
    ligs_unique : list
        List of unique ligands
    """

    # get unique ligands based on ligand names
    ligs_unique = []
    ligs_repeat = []
    for index, templig in enumerate(ligand_list):
        temp_lig_name = templig.name
        if temp_lig_name not in ligs_repeat:
            ligs_unique.append(ligand_list[index])
            ligs_repeat.append(temp_lig_name)
    return ligs_unique

def write_mol2(ligs_unique, file_info):
    """
    Write a MOL2 file for each unique ligand in the list of ligands.

    Parameters
    ----------
    ligs_unique : List
        List of unique ligands
    file_info : File_Info object

    Returns
    -------
    ligs : list
        List of ligand names
    filenames : list
        List of filenames for each ligand
    """

    global ligs # list of names for each ligand
    global filenames # list of resulting file names for each ligand
    ligs = []
    filenames = []
    previous_atoms = 0
    for unique_ind, unique_lig in enumerate(ligs_unique):
        # add ligand name to lig list and create a mol2 file for it
        ligs.append(unique_lig.name)
        filename = "data/MOL2_files/" + str(unique_lig.name) + ".mol2"
        filenames.append(filename)
        infile = open(filename, "w") 
        # write molecule info for ligand mol2 file
        tripos_mols = []
        for line in unique_lig.lines_mol:
            tripos_mols.append(line)
        # update ligand info line (contains atom count, bond count, etc) to be correct for separated ligand (i.e. make sure it doesnt contain counts for all ligands combined)
        temp_mol = re.split(r"(\s+)", tripos_mols[2])
        temp_mol[2] = unique_lig.num_atoms
        temp_mol[4] = unique_lig.num_bonds
        new_mol = ''.join(str(x) for x in temp_mol)
        tripos_mols[2] = new_mol
        tripos_mols.append("\n")
        # write atom info for ligand mol2 file
        tripos_atoms = ["@<TRIPOS>ATOM\n"]
        counter_atom = 1
        atom1 = unique_lig.lines_atom[0] # lower limit/starting value for atom numbers
        atom2 = unique_lig.lines_atom[-1] # upper limit for atom numbers
        while atom1 <= atom2:
            # get line in original combined mol2 file corresponding to index of atom1
            temp_atom = re.split(r"(\s+)", file_info.lines_atoms[atom1])
            temp_atom = temp_atom[:-1]
            original_values = file_info.lines_atoms[atom1].split()
            temp_atom[2] = str(counter_atom)
            # if atom number has changed length, adjust spacing
            if len(temp_atom[2]) > 1 and (len(temp_atom[2]) != len(original_values[0])):
                len_space = len(temp_atom[1])
                temp_atom[1] = temp_atom[1][:(len_space + 1 - len(temp_atom[2]))]
            new_atom = ''.join(str(x) for x in temp_atom)
            tripos_atoms.append(new_atom)
            counter_atom += 1
            atom1 += 1
        # write bonds info for ligand mol2 file
        tripos_bonds = ["@<TRIPOS>BOND\n"]
        counter_bond = 1
        bond1 = unique_lig.lines_bond[0] # lower limit/starting value for bond numbers
        bond2 = unique_lig.lines_bond[1] # upper limit for bond numbers
        max_bond_index = file_info.lines_bonds[bond2].split()
        # determine if atom indexes in bond lines need to be renumbered for ligand
        renumber_bond_atoms = False
        if ((max(int(max_bond_index[1]), int(max_bond_index[2])) > unique_lig.num_atoms) and unique_ind > 0):
            renumber_bond_atoms = True
        while bond1 <= bond2:
            # get line in original combined mol2 file corresponding to index of bond1
            temp_bond = re.split(r"(\s+)", file_info.lines_bonds[bond1])
            temp_bond = temp_bond[:-1]
            original_values = file_info.lines_bonds[bond1].split()
            temp_bond[2] = str(counter_bond)
            # if bond number has changed length, adjust spacing
            if (len(temp_bond[2]) != len(original_values[0])):
                len_diff = len(original_values[0]) - len(temp_bond[2])
                len_space = len(temp_bond[1])
                if len_diff > 0:
                    temp_bond[1] = temp_bond[1] + (" " * (len_diff))
                else:
                    temp_bond[1] = temp_bond[1][:(len_space + 1 - len_diff)]
            # confirm that numbers for atoms in bond are consistant with atom numbering system in atom info
            if (renumber_bond_atoms):
                temp_bond[4] = str(int(temp_bond[4]) - previous_atoms)
                temp_bond[6] = str(int(temp_bond[6]) - previous_atoms)
            # if the length of the number corresponding to the first atom in the bond has changed, adjust spacing
            if (len(temp_bond[4]) != len(original_values[1])):
                len_diff = len(original_values[1]) - len(temp_bond[4])
                len_space = len(temp_bond[3])
                if len_diff > 0:
                    temp_bond[3] = temp_bond[3] + (" " * (len_diff))
                else:
                    temp_bond[3] = temp_bond[3][:(len_space + 1 - len_diff)]
            # if the length of the number corresponding to the second atom in the bond has changed, adjust spacing
            if (len(temp_bond[6]) != len(original_values[2])):
                len_diff = len(original_values[2]) - len(temp_bond[6])
                len_space = len(temp_bond[5])
                if len_diff > 0:
                    temp_bond[5] = temp_bond[5] + (" " * (len_diff))
                else:
                    temp_bond[5] = temp_bond[5][:(len_space + 1 - len_diff)]
            new_bond = ''.join(str(x) for x in temp_bond)
            tripos_bonds.append(new_bond)
            counter_bond += 1
            bond1 += 1
        previous_atoms = previous_atoms + unique_lig.num_atoms
        # write file
        infile.writelines(tripos_mols)
        infile.writelines(tripos_atoms)
        infile.writelines(tripos_bonds)
        infile.close()
    return ligs, filenames

def separate_mol2_ligs(filename = '', name_vals = {}, current_dir = os.getcwd()):
    """
    Split a ligand file into individual ligands and write them to separate MOL2 files.

    Parameters
    ----------
    filename : String
        Filename of the ligand file to be split and parsed.
    name_vals : dict

    Returns
    -------
    ligs : list
        List of ligand names
    filenames : list
        List of filenames for each ligand
    """

    #current_dir = os.getcwd()
    ligand_file = os.path.join(current_dir, filename)
    file_info = get_mol2_info(ligand_file)
    ligand_list = get_ligands(file_info, name_vals)
    ligs_unique = find_ligands_unique(ligand_list)
    ligs, filenames = write_mol2(ligs_unique, file_info)
    return ligs, filenames
