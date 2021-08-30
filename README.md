
## mmCIF files

wwPDB provides three kinds of PDBx/mmCIF files:
* coordinate files (models, "normal" mmCIF)
* structure factors (experimental data, SF-mmCIF)
* [Chemical Component Dictionary](http://www.wwpdb.org/data/ccd) with
  the main file named `components.cif`.

How quickly these files can be parsed?

For big files, we test `components.cif` from Aug 2021 - 327 MB,
coordinate file 3j3q.cif - 230 MB,
and reflection file 4v9p - 248 MB.

These three files are pretty big (although the PDB has 10x bigger SF-mmCIF
files). To add more representative files I used two entries from
[MMTF benchmark](https://github.com/rcsb/mmtf-python-benchmark/):
4fxz (428KB) and 1cjb (836KB) that represent structures around the 50
and 75 percentile of the PDB size distribution
(no. 50 from the corresponding `sample_NN.csv` files there).

The data files can be downloaded from wwPDB:

    DATA="ftp://ftp.wwpdb.org/pub/pdb/data"
    wget $DATA/monomers/components.cif.gz
    wget $DATA/structures/divided/mmCIF/j3/3j3q.cif.gz
    wget $DATA/structures/divided/structure_factors/v9/r4v9psf.ent.gz
    wget $DATA/structures/divided/mmCIF/fx/4fxz.cif.gz
    wget $DATA/structures/divided/mmCIF/cj/1cjb.cif.gz
    gunzip *.gz

Note: benchmarks made by an author of one of the benchmarked programs
are always suspicious. This benchmark was prepared by the author of
[Gemmi](https://project-gemmi.github.io/).

## CIF parsing

In this section I benchmarked function calls and helper programs that work
with CIF files on the syntactic level. The programs do different things,
so I compare apples to oranges, but it gives you some idea what to expect.

The scripts used here are in the ``read-cif`` subdirectory.
They either call commands:

* `gemmi-validate` - parses and copies all the data into a DOM structure
* `gemmi-validate-fast` - parses a file w/o copying any data
* `cif_api` - runs `cif2_syncheck` from cif_api, as in a benchmark in
  [this paper](http://dx.doi.org/10.1107/S1600576715021883).
* `cif_api_fast` - the same, but with the `-f` option (does not create DOM)

or are Python scripts:

* `gemmi-read` - reads the CIF file from Python
* `pycodcif` - runs `parse` from [pycodcif](https://github.com/merkys/pycodcif)
* `iotbx-read` - calls `iotbx.cif.reader()` from
  [cctbx/iotbx](https://cctbx.github.io/iotbx/) (Python)
* `py-mmcif` - reads using mmcif.io.PdbxReader
  from [py-mmcif](https://github.com/rcsb/py-mmcif) (developed at RCSB)
* `py-mmcif-iab` - reads using mmcif.io.IoAdapterCore
  from [py-mmcif](https://github.com/rcsb/py-mmcif)
* `pdbecif` - uses Python parser from
  [pdbecif](https://github.com/PDBeurope/pdbecif) (developed at PDBe).


The benchmark was run using the `run.sh` script from this repository:

    for prog in read-cif/*; do ./run.sh $prog; done

Each combination of script/program and cif file was timed 10 times
and the fastest time was reported.
The benchmark was run on a Linux system, CPU i7-4790, 16GB RAM with
12GB limit on the program memory (`ulimit -v 12582912`).
The libraries were installed from binaries (mostly from PyPI)
or compiled with GCC 7 with default options (-O2 or -O3).

### Run time (seconds) and peak memory (MB)

|       program         | 4fxz | mem  | 1cjb | mem   | 3j3q  | mem   | r4v9psf | mem   |  CCD   | mem   |
| --------------------- | ---: | ---: | ---: | ----: | ----: | ----: | ------: | ----: | -----: | ----: |
| `gemmi-validate`      | 0.01 |  8.5 | 0.01 |  13.0 |  5.0  | 2278  |    3.6  | 2312  |   5.1  | 2331  |
| `gemmi-validate-fast` | 0.00 |  4.3 | 0.00 |   4.4 |  1.7  |  237  |    1.5  |  254  |   2.0  |  334  |
| `cif_api`             | 2.4  |  9.8 | 5.20 |   9.8 | > 1h  |   10  |  635.6  |    9  | 587.0  |    9  |
| `cif_api_fast`        | 0.01 |  6.2 | 0.02 |   6.1 |  7.4  |  7.7  |    5.2  |    6  |   9.4  |    6  |
| `gemmi-read`          | 0.17 | 42.0 | 0.18 |  47.0 |  7.8  | 3369  |    6.0  | 2493  |   8.3  | 3207  |
| `pycodcif`            | 0.27 | 34.0 | 0.52 |  58.0 |  OOM  |       |  111.3  | 9851  |  OOM   |       |
| `iotbx-read`          | 0.34 | 98.0 | 0.40 | 120.0 |  OOM  |       |   28.5  | 8771  |  OOM   |       |
| `py-mmcif`            | 0.16 | 20.9 | 0.26 |  25.6 | 65.5  | 3217  |   55.3  | 1939  |  72.8  | 3291  |
| `py-mmcif-iab`        | 0.11 | 26.7 | 0.16 |  35.8 | 38.7  | 6008  |   26.1  | 3897  |  53.6  | 6535  |
| `pdbecif`             | 0.05 | 14.9 | 0.07 |  18.9 | 15.6  | 3025  |   11.1  | 1942  |  41.6  | 2671  |

OOM = out-of-memory error

For comparison (scripts in the `alt` subdirectory):
* decoding [1cjb MMTF file](http://mmtf.rcsb.org/v1.0/full/1cjb.mmtf.gz)
  with [mmtf-python](https://github.com/rcsb/mmtf-python) takes 0.11s
  (32MB of memory),
* parsing
  [1cjb mmJSON](https://pdbj.org/rest/downloadPDBfile?id=1CJB&format=mmjson-all)
  with Python built-in parser takes 0.03s (17MB of memory).

## Creating a structural model

Here we benchmark reading
[coordinate mmCIF files](http://gemmi.readthedocs.io/en/latest/mol.html#pdbx-mmcif-format)
and interpreting their content as a structural model,
which usually involves building a model-chain-residue-atom hierarchy.

The scripts that are run are in the ``read-model`` subdirectory.
They all happen to be Python scripts:

* `gemmi-structure` - calls `gemmi.read_structure()` from Python.
  Internally, it first copies all the data into DOM structure, and then
  creates a hierarchy copying the data again.
* `biopython` - calls `MMCIFParser().get_structure()`
  from [BioPython](https://biopython.org/)
* `biopython-fast` - calls `FastMMCIFParser().get_structure()`
  (BioPython has two parsers - only the slower one aims
  to parse mmCIF files correctly)
* `clipper-python` - calls `clipper.MMDBfile().read_file()` from
  [clipper-python](https://github.com/clipper-python/clipper-python)
* `iotbx-pdb` - calls `iotbx.pdb.input()` from
  [cctbx/iotbx](https://cctbx.github.io/iotbx/)
* `atomium` - calls `atomium.open()` from [atomium](github.com/samirelanduk/atomium)

These benchmarks can be run only with coordinate files.
Here I use only two of them: 1cjb.cif and 3j3q.cif:

    for prog in read-model/*; do ./run-one.sh $prog 1cjb.cif; done
    for prog in read-model/*; do ./run-one.sh $prog 3j3q.cif; done

|       program         | 1cjb | mem  | 3j3q  |  mem  |
| --------------------- | ---: | ---: | ----: | ----: |
| `gemmi-structure`     | 0.19 |  48  |  11.0 |  4085 |
| `biopython`           | 0.55 |  53  | 138.8 |  6197 |
| `biopython-fast`      | 0.35 |  55  |  67.0 |  6986 |
| `clipper-python`      | ERR  |      |  55.6 |  2854 |
| `iotbx-pdb`           | 0.43 | 119  |  ERR  |       |
| `atomium`             | 0.85 |  96  | 108.5 | 10017 |

The table reports elapsed time in seconds and peak memory in MB.

For comparison:
* parsing 1cjb MMTF file with BioPython parser takes 0.26s and 47MB mem.

## Other benchmarks

Parsing small CIF files: https://github.com/cod-developers/CIF-parsers

Parsing PDB files: https://github.com/jgreener64/pdb-benchmarks  
(it doesn't include Gemmi, but parsing 1HTQ PDB file in Gemmi takes
about 0.5s, it's 3-4x faster than parsing corresponding mmCIF file).

## Thoughts

mmJSON would be the format of choice in computing if it was one of the
formats supported by the wwPDB. Currently wwPDB provides coordinates in
3 formats: PDBx/mmCIF (master format), PDB (legacy format)
and PDBML (XML-based one).
