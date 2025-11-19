ligandsplitter
==============================
[//]: # (Badges)
[![GitHub Actions Build Status](https://github.com/leesch27/ligandsplitter/workflows/CI/badge.svg)](https://github.com/leesch27ligandsplitter/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/leesch27/ligandsplitter/branch/main/graph/badge.svg)](https://codecov.io/gh/leesch27/ligandsplitter/branch/main)


A Python package for creating, splitting, and validating ligand files

### Installation

1. Manual
```
git clone https://github.com/leesch27/ligandsplitter.git
```
2. PyPi
```
pip install ligandsplitter
```

### Usage
ligandsplitter contains five main modules that aid in the generation, search and retrieval, isolation, and validation of ligands in the form of MOL2 files. 

#### Ligand Generation
When provided a SMILES string representation of a ligand, MOL2 files of that ligand can be created. 

#### Ligand Search and Retrieval
Using rcsb-api, ligands can be searched using RCSB PDB's Advanced Search feature by user-defined critera.

#### Ligand Isolation/"Splitting" from Receptor File
Provided a PDB/CIF file of a macromolecule containing at least one ligand, ligands can be extracted and written to individual MOL2 files. 

#### Ligand Validation
From a list of SMILES strings, unique ligands can be determined and are checked to ensure they do not violate any atomic or bonding rules.


### Jupyter Notebooks
ligandsplitter was initially made to enhance a series of notebooks that explore molecular docking using Jupyter notebooks. To view this series, known as basil_dock, you can <a href="https://github.com/leesch27/basil_dock">click here</a>.

### Copyright

Copyright (c) 2024, Lee Schoneman


#### Acknowledgements
 
Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.10.
