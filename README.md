
## mmCIF files

wwPDB provides three kinds of PDBx/mmCIF files:
* coordinate files (models, "normal" mmCIF)
* structure factors (experimental data, SF-mmCIF)
* [Chemical Component Dictionary](http://www.wwpdb.org/data/ccd) with
  the main file named `components.cif`.

How quickly software libraries can parse these files?

As of May 2018 `components.cif` has 247,493,093 bytes.
The largest coordinate file is slightly smaller:
 3j3q.cif  has 241,631,935 bytes.
To make the numbers easy to compare I used a script
(`find_similar.py` from this repo) to find a SF file that is also similar
in size to `components.cif`. 4v9p has 260,351,280 bytes (the biggest
SF file - 6cgv - is 50% bigger).

The data files can be downloaded from wwPDB:

    DATA="ftp://ftp.wwpdb.org/pub/pdb/data"
    wget $DATA/monomers/components.cif.gz
    wget $DATA/structures/divided/mmCIF/j3/3j3q.cif.gz
    wget $DATA/structures/divided/structure_factors/v9/r4v9psf.ent.gz
    gunzip *.gz


## CIF parsing

The ``read-cif`` subdirectory has scripts that parse CIF files:

* gemmi-validate-fast - only parses a file
* gemmi-validate - parses and copies all the data into a DOM structure

The benchmark was run using the `run.sh` script from this repository:

    for prog in read-model/*; do ./run.sh $prog; done

Each combination of script/program and cif file was timed 10 times
and the fastest time was reported.

TODO: add other cif parsers (iotbx, COD::CIF::Parser, cif_api, pdbx)

TODO: try MMTF and mmJSON

TODO: results

## Creating a structural model

The ``read-model`` subdirectory has scripts that read cif files and
create structural models:

* gemmi-structure - a python script that calls `gemmi.read_structure`.
  Internally, it first copies all the data into DOM structure, and then
  reads it to create a Model-Chain-Residue-Atom hierarchy (copying the data
  again).

These benchmarks can be run only with the 3j3q.cif file:

    for prog in read-model/*; do ./run-one.sh $prog 3j3q.cif; done

TODO: add other parsers (iotbx, clipper-python, BioPython)

TODO: results
