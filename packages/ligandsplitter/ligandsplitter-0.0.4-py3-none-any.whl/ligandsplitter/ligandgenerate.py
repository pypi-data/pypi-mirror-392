"""Functions used to search for and create ligands."""
from rdkit import Chem
from openbabel import pybel
import ipywidgets as widgets
from ipywidgets import Text, Layout, Label, FileUpload, Box, HBox, Dropdown, Output
import requests
import rcsbapi
from rcsbapi.search import AttributeQuery, Attr, TextQuery, ChemSimilarityQuery
from IPython.display import display

def create_search_for_expo():
    """
    Create a search form for ligands in the RCSB PDB database.
    Uses ipywidgets to create dropdowns and text boxes for user input. To be used in Jupyter Notebooks.

    Parameters
    ----------
    None

    Returns
    -------
    attr_bool : dict
        Dictionary of attribute booleans.
    attr_val : dict
        Dictionary of attribute values.
    form_items1 : list
        List of form items for the first half of the form.
    form_items2 : list
        List of form items for the second half of the form.
    """

    global attr_bool
    global attr_val
    chem_types = ["D-beta-peptide, C-gamma linking",
                "D-gamma-peptide, C-delta linking",
                "D-peptide COOH carboxy terminus",
                "D-peptide NH3 amino terminus",
                "D-peptide linking",
                "D-saccharide",
                "D-saccharide, alpha linking",
                "D-saccharide, beta linking",
                "DNA OH 3 prime terminus",
                "DNA OH 5 prime terminus",
                "DNA linking",
                "L-DNA linking",
                "L-RNA linking",
                "L-beta-peptide, C-gamma linking",
                "L-gamma-peptide, C-delta linking",
                "L-peptide COOH carboxy terminus",
                "L-peptide NH3 amino terminus",
                "L-peptide linking",
                "L-saccharide",
                "L-saccharide, alpha linking",
                "L-saccharide, beta linking",
                "RNA OH 3 prime terminus",
                "RNA OH 5 prime terminus",
                "RNA linking",
                "non-polymer",
                "other",
                "peptide linking",
                "peptide-like",
                "saccharide"]
    form_item_layout = Layout(
    display='flex',
    flex_flow='row',
    justify_content='space-between')
    style = {'description_width': 'initial'}

    attr1 = Dropdown(options = ["No", "Yes"], description = 'Search by Chemical Name?:', style = style)
    attr2 = Dropdown(options = ["No", "Yes"], description = 'Search by Chemical Name Synonym?', style = style)
    attr3 = Dropdown(options = ["No", "Yes"], description = 'Search by Chemical ID?', style = style)
    attr4 = Dropdown(options = ["No", "Yes"], description = 'Search by Chemical Type?', style = style)
    attr5 = Dropdown(options = ["No", "Yes"], description = 'Search by Chemical Brand Name?', style = style)
    attr6 = Dropdown(options = ["No", "Yes"], description = 'Search by Formula Similarity?', style = style)
    attr7 = Dropdown(options = ["No", "Yes"], description = 'Search by Structure Similarity?', style = style)

    attr1_val = Text(value = '', placeholder='Type Chemical Name Here (e.g. alanine)', disabled=False)
    attr2_val = Text(value = '', placeholder='Type Synonym Here (e.g. acetylsalicylic acid)', disabled=False)
    attr3_val = Text(value = '', placeholder='Type RCSB Chemical ID Here (e.g. AIN)', disabled=False)
    attr4_val = Dropdown(options = chem_types, description = 'Select Chemical Type', style = style)
    attr5_val = Text(value = '', placeholder='Type DrugBank Brand Name Here (e.g. Aspirin)', disabled=False)
    attr6_val = Text(value = '', placeholder='Type Ligand Formula Here (e.g. C9H8O4)', disabled=False)
    attr7_val = Text(value = '', placeholder='Type Ligand SMILES Here', disabled=False)

    attr_bool = {"attr1": attr1, "attr2": attr2, "attr3": attr3, "attr4": attr4, "attr5": attr5, "attr6": attr6, "attr7": attr7}
    attr_val = {"attr1_val": attr1_val, "attr2_val": attr2_val, "attr3_val": attr3_val, "attr4_val": attr4_val, "attr5_val": attr5_val, "attr6_val": attr6_val, "attr7_val": attr7_val}

    form_items1 = [attr1, attr2, attr3, attr4, attr5, attr6, attr7]
    form_items2 = [attr1_val, attr2_val, attr3_val, attr4_val, attr5_val, attr6_val, attr7_val]

    return attr_bool, attr_val, form_items1, form_items2


def create_search_for_protein():
    """
    Create a search form for proteins in the RCSB PDB database.
    Uses ipywidgets to create dropdowns and text boxes for user input. To be used in Jupyter Notebooks.

    Parameters
    ----------
    None

    Returns
    -------
    attr_bool : dict
        Dictionary of attribute booleans.
    attr_val : dict
        Dictionary of attribute values.
    attr_comp : dict
        Dictionary of comparison values.
    form_items1 : list
        List of form items containing queries to search by.
    form_items2 : list
        List of form items containing target values for queries.
    form_items3 : list
        List of form items containing comparison operators for queries.
    """

    global attr_bool
    global attr_val
    form_item_layout = Layout(
    display='flex',
    flex_flow='row',
    justify_content='space-between')
    style = {'description_width': 'initial'}

    attr1 = Dropdown(options = ["No", "Yes"], description = 'Search by Enzyme Classification Name?:', style = style)
    attr2 = Dropdown(options = ["No", "Yes"], description = 'Search by Enzyme Classification Number?', style = style)
    attr3 = Dropdown(options = ["No", "Yes"], description = 'Search by Number of Protein Chains?', style = style)
    attr4 = Dropdown(options = ["No", "Yes"], description = 'Search by Length of Sequence?', style = style)
    attr5 = Dropdown(options = ["No", "Yes"], description = 'Search by Molecular Weight?', style = style)

    attr1_val = Text(value = '', placeholder='Type Enzyme Classification Name', disabled=False)
    attr2_val = Text(value = '', placeholder='Type Enzyme Classification Number', disabled=False)
    attr3_val = Text(value = '', placeholder='Type Number of Protein Chains Here', disabled=False)
    attr4_val = Text(value = '', placeholder='Type Length of Sequence Here', disabled=False)
    attr5_val = Text(value = '', placeholder='Type Molecular Weight Here', disabled=False)

    comp1_val = Dropdown(options = ["is", "is not empty"], description = 'Select Comparison Operator:', style = style)
    comp2_val = Dropdown(options = ["is any of", "is not empty"], description = 'Select Comparison Operator:', style = style)
    comp3_val = Dropdown(options = ["==", ">", ">=", "<", "<="], description = 'Select Comparison Operator:', style = style)
    comp4_val = Dropdown(options = ["==", ">", ">=", "<", "<="], description = 'Select Comparison Operator:', style = style)
    comp5_val = Dropdown(options = ["==", ">", ">=", "<", "<="], description = 'Select Comparison Operator:', style = style)

    attr_bool = {"attr1": attr1, "attr2": attr2, "attr3": attr3, "attr4": attr4, "attr5": attr5}
    attr_val = {"attr1_val": attr1_val, "attr2_val": attr2_val, "attr3_val": attr3_val, "attr4_val": attr4_val, "attr5_val": attr5_val}
    attr_comp = {"comp1_val": comp1_val, "comp2_val": comp2_val, "comp3_val": comp3_val, "comp4_val": comp4_val, "comp5_val": comp5_val}

    form_items1 = [attr1, attr2, attr3, attr4, attr5]
    form_items2 = [attr1_val, attr2_val, attr3_val, attr4_val, attr5_val]
    form_items3 = [comp1_val, comp2_val, comp3_val, comp4_val, comp5_val]
    return attr_bool, attr_val, attr_comp, form_items1, form_items2, form_items3

def display_expo_form(form_items1, form_items2, form_items3 = []):
    """
    Display form generated by create_search_for_expo.
    Uses ipywidgets to create dropdowns and text boxes for user input. To be used in Jupyter Notebooks.

    Parameters
    ----------
    form_items1 : list
        List of form items containing queries to search by.
    form_items2 : list
        List of form items containing target values for queries.
    form_items3 : list (Optional)
        List of form items containing comparison operators for queries.

    Returns
    -------
    Form
    """

    form_1 = Box(form_items1, layout = Layout(
        display = 'flex',
        flex_flow = 'column',
        border = 'solid 2px',
        align_items = 'stretch',
        width = '50%'))
    form_2 = Box(form_items2, layout = Layout(
        display = 'flex',
        flex_flow = 'column',
        border = 'solid 2px',
        align_items = 'stretch',
        width = '50%'))
    if len(form_items3) > 0:
        form_3 = Box(form_items3, layout = Layout(
        display = 'flex',
        flex_flow = 'column',
        border = 'solid 2px',
        align_items = 'stretch',
        width = '50%'))
        form = HBox([form_1, form_2, form_3])
    else:
        form = HBox([form_1, form_2])

    return form

def create_ligands_from_expo(attr_bool, attr_val):
    """
    Create a search query for ligands in the RCSB PDB database based on user input.
    Uses ipywidgets to create dropdowns and text boxes for user input. To be used in Jupyter Notebooks.

    Parameters
    ----------
    attr_bool : dict
        Dictionary of attribute booleans.
    attr_val : dict
        Dictionary of attribute values.

    Returns
    -------
    result_lig : list
        List of ligands that match the search criteria.
    query : str
        Query string used to search for ligands.
    """

    bool_vals = {}
    val_vals = {}
    for value in attr_bool.keys():
        bool_vals[value] = attr_bool[value].value
    for value in attr_val.keys():
        val_vals[value] = attr_val[value].value
    bools = list(bool_vals.values())
    values = list(val_vals.values())
    q1 = AttributeQuery(attribute = "chem_comp.name", operator = "exact_match", value = values[0])
    q2 = AttributeQuery(attribute = "rcsb_chem_comp_synonyms.name", operator = "contains_phrase", value = values[1], service = "text_chem")
    q3 = AttributeQuery(attribute = "rcsb_id", operator = "exact_match", value = values[2], service = "text_chem")
    q4 = AttributeQuery(attribute = "chem_comp.type", operator = "exact_match", value = values[3])
    q5 = AttributeQuery(attribute = "drugbank_info.brand_names", operator = "contains_phrase", value = values[4])
    q6 = ChemSimilarityQuery(query_type = "formula", value = values[5])
    q7 = ChemSimilarityQuery(query_type = "descriptor", descriptor_type = "SMILES", match_type="fingerprint-similarity", value = values[6])
    
    attr_list = [q1, q2, q3, q4, q5, q6, q7]
    positives = []
    global query
    for number, value in enumerate(bools):
        if value == "Yes":
            positives.append(attr_list[number])
    if len(positives) > 0:
        if len(positives) == 1:
            query = positives[0]
        else:
            query = ' & '.join(x for x in positives)
    else:
        print("Invalid.")
    result_lig = list(query())
    return result_lig, query


def create_proteins(attr_bool, attr_val, attr_comp):
    """
    Create a search query for proteins in the RCSB PDB database based on user input.
    Uses ipywidgets to create dropdowns and text boxes for user input. To be used in Jupyter Notebooks.

    Parameters
    ----------
    attr_bool : dict
        Dictionary of attribute booleans.
    attr_val : dict
        Dictionary of attribute values.
    attr_comp : dict
        Dictionary of comparison values.

    Returns
    -------
    result_lig : list
        List of proteins that match the search criteria.
    query : str
        Query string used to search for receptors.
    """

    bool_vals = {}
    val_vals = {}
    comp_vals = {}

    for value in attr_bool.keys():
        bool_vals[value] = attr_bool[value].value
    for value in attr_val.keys():
        val_vals[value] = attr_val[value].value
    #translate initial comparison symbols into terms needed for search
    for value in attr_comp.keys():
        comp_vals_initial = attr_comp[value].value
        if comp_vals_initial == "==":
            comp_vals[value] = "equals"
        elif comp_vals_initial == ">":
            comp_vals[value] = "greater"
        elif comp_vals_initial == ">=":
            comp_vals[value] = "greater_or_equal"
        elif comp_vals_initial == "<":
            comp_vals[value] = "less"
        elif comp_vals_initial == "<=":
            comp_vals[value] = "less_or_equal"
        elif comp_vals_initial == "is":
            comp_vals[value] = "exact_match"
        elif comp_vals_initial == "is not empty":
            comp_vals[value] = "exists"
        elif comp_vals_initial == "is any of":
            comp_vals[value] = "in"
  
    bools = list(bool_vals.values())
    values = list(val_vals.values())
    comps = list(comp_vals.values())

    q0 = AttributeQuery(attribute = "rcsb_entry_info.selected_polymer_entity_types", operator = "exact_match", value = "Protein (only)")
    if bools[0] == "Yes":
        q1 = AttributeQuery(attribute = "rcsb_polymer_entity.rcsb_ec_lineage.name", operator = comps[0], value = values[0])
    else:
        q1 = AttributeQuery(attribute = "rcsb_polymer_entity.rcsb_ec_lineage.name", operator = "equals", value = "")
    if bools[1] == "Yes":
        q2 = AttributeQuery(attribute = "rcsb_polymer_entity.rcsb_ec_lineage.id", operator = comps[1], value = values[1])
    else:
        q2 = AttributeQuery(attribute = "rcsb_polymer_entity.rcsb_ec_lineage.id", operator = "equals", value = "")
    if bools[2] == "Yes":
        q3 = AttributeQuery(attribute = "rcsb_entry_info.polymer_entity_count_protein", operator = comps[2], value = int(values[2]))
    else:
        q3 = AttributeQuery(attribute = "rcsb_entry_info.polymer_entity_count_protein", operator = "equals", value = 0)
    if bools[3] == "Yes":
        q4 = AttributeQuery(attribute = "entity_poly.rcsb_sample_sequence_length", operator = comps[3], value = int(values[3]))
    else:
        q4 = AttributeQuery(attribute = "entity_poly.rcsb_sample_sequence_length", operator = "equals", value = 0)
    if bools[4] == "Yes":
        q5 = AttributeQuery(attribute = "rcsb_entry_info.molecular_weight", operator = comps[4], value = float(values[4]))
    else:
        q5 = AttributeQuery(attribute = "rcsb_entry_info.molecular_weight", operator = "equals", value = 0)
    
    attr_list = [q1, q2, q3, q4, q5]
    positives = [q0]
    global query
    for number, value in enumerate(bools):
        if value == "Yes":
            positives.append(attr_list[number])
    if len(positives) > 0:
        if len(positives) == 1:
            query = positives[0]
        else:
            current_len = 1
            query = positives[0]
            while current_len < len(positives):
                query = query & positives[current_len]
                current_len += 1
    else:
        print("Invalid.")
    result = list(query())
    return result, query

def create_ligands_from_smiles(num_of_ligs):
    """
    Create a form to input ligand names and SMILES strings.
    Uses ipywidgets to create dropdowns and text boxes for user input. To be used in Jupyter Notebooks.

    Parameters
    ----------
    num_of_ligs : int
        Number of ligands to create.

    Returns
    -------
    names_for_ligs : dict
        Dictionary of ligand names.
    smiles_for_ligs : dict
        Dictionary of ligand SMILES strings.
    form_items1 : list
        List of form items for the first half of the form.
    form_items2 : list
        List of form items for the second half of the form.
    """

    form_item_layout = Layout(display='flex',flex_flow='row',justify_content='space-between')
    global names_for_ligs
    global smiles_for_ligs
    names_for_ligs = {}
    smiles_for_ligs = {}
    labels_name = {}
    labels_smiles = {}
    number = 1
    while number <= num_of_ligs.value:
        temp_name = "name" + str(number)
        temp_smile = "scratch" + str(number)
        names_for_ligs[temp_name] = Text(value = '', placeholder=f'Type the name of ligand {number} with no spaces', disabled=False)
        smiles_for_ligs[temp_smile] = Text(value = '', placeholder=f'Type in ligand {number} using SMILE codes', disabled=False)
        labels_name[temp_name] = Label(value=f'Name of ligand {number}')
        labels_smiles[temp_smile] = Label(value=f'SMILES string for ligand {number}')
        number += 1
    form_items1 = []
    form_items2 = []
    for list_number, name in enumerate(names_for_ligs):
        new_number = list_number + 1
        form_items1.append(Box([labels_name["name" + str(new_number)], names_for_ligs[name]], layout=form_item_layout))
        
    for list_number, smiles in enumerate(smiles_for_ligs):
        new_number = list_number + 1
        form_items2.append(Box([labels_smiles["scratch" + str(new_number)], smiles_for_ligs[smiles]], layout=form_item_layout))
    return names_for_ligs, smiles_for_ligs, form_items1, form_items2

def display_smiles_form(num_of_ligs, form_items1, form_items2):
    """
    Display form generated by create_ligands_from_smiles.
    Uses ipywidgets to create dropdowns and text boxes for user input. To be used in Jupyter Notebooks.

    Parameters
    ----------
    num_of_ligs : int
        Number of ligands to create.
    form_items1 : list
        List of form items for the first half of the form.
    form_items2 : list
        List of form items for the second half of the form.

    Returns
    -------
    Form
    """

    form1 = Box(form_items1, layout = Layout(
        display = 'flex',
        flex_flow = 'column',
        border = 'solid 2px',
        align_items = 'stretch',
        width = '50%'
    ))
    form2 = Box(form_items2, layout = Layout(
        display = 'flex',
        flex_flow = 'column',
        border = 'solid 2px',
        align_items = 'stretch',
        width = '50%'
    ))

    form = HBox([form1, form2])
    return form

def create_mols_from_smiles(num_of_ligs, names_for_ligs, smiles_for_ligs, out_filename='InputMols.mol2'):
    """
    Generate ligand molecules from SMILES strings and save them in MOL2 format.

    Parameters
    ----------
    num_of_ligs : int
        Number of ligands to create.
    out_filename : str, optional
        Name of the output file to save the generated molecules in MOL2 format. Default is 'data/MOL2_files/InputMols.mol2'.

    Returns
    -------
    name_vals : dict
        Dictionary of ligand names.
    scratch_vals : dict
        Dictionary of ligand SMILES strings.
    """

    name_vals = {}
    scratch_vals = {}
    name_keys = list(names_for_ligs.keys())
    scratch_keys = list(smiles_for_ligs.keys())
    for value in name_keys:
        name_vals[value] = names_for_ligs[value]

    for value in scratch_keys:
        scratch_vals[value] = smiles_for_ligs[value]
    
    smiles = []
    smile_names = []
    a = 0
    while a < num_of_ligs:
        lig_name = name_vals[name_keys[a]]
        lig_scratch = scratch_vals[scratch_keys[a]]
        lig_test = Chem.MolFromSmiles(lig_scratch)
        if (len(lig_scratch) < 2000) & (lig_test is not None):
            smile_names.append(lig_name)
            smiles.append(lig_scratch)
        a += 1
    out=pybel.Outputfile(filename = f"data/MOL2_files/{out_filename}",format='mol2',overwrite=True) # change output file name to a var to allow for users to choose name
    for index, smi in enumerate(smiles):
        mol = pybel.readstring(string=smi,format='smiles')
        mol.title= str(smile_names[index])
        mol.make3D('mmff94s')
        mol.localopt(forcefield = 'mmff94s', steps = 500)
        out.write(mol)
    out.close()
    return name_vals, scratch_vals
