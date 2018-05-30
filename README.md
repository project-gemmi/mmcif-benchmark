
## mmCIF files

wwPDB provides three kinds of PDBx/mmCIF files:
* coordinate files (models, "normal" mmCIF)
* structure factors (experimental data, SF-mmCIF)
* [Chemical Component Dictionary](http://www.wwpdb.org/data/ccd) with
  the main file named `components.cif`.

How quickly these files can be parsed?

As of May 2018 `components.cif` has 247,493,093 bytes.
The largest coordinate file is slightly smaller:
3j3q.cif  has 241,631,935 bytes.
To make the numbers easy to compare I used a script
(`find_similar.py` from this repo) to find a SF file that is also similar
in size to `components.cif`. 4v9p has 260,351,280 bytes (the biggest
SF file - 6cgv - is 50% bigger).

All these files are pretty big. To add more representative files
I used two entries from
[MMTF benchmark](https://github.com/rcsb/mmtf-python-benchmark/):
4fxz (428KB) and 1cjb (836KB) that represent structures around the 50
and 75 percentile of the PDB size distribution
(no. 50 from corresponding `sample_NN.csv` file there).

The data files can be downloaded from wwPDB:

    DATA="ftp://ftp.wwpdb.org/pub/pdb/data"
    wget $DATA/monomers/components.cif.gz
    wget $DATA/structures/divided/mmCIF/j3/3j3q.cif.gz
    wget $DATA/structures/divided/structure_factors/v9/r4v9psf.ent.gz
    wget $DATA/structures/divided/mmCIF/fx/4fxz.cif.gz
    wget $DATA/structures/divided/mmCIF/cj/1cjb.cif.gz
    gunzip *.gz


## CIF parsing

In this section I benchmarked function calls and helper programs that work
with CIF files on the syntactic level. The programs do different things,
so I compare apples to oranges, but it gives you some idea what to expect.

The scripts that are run are in the ``read-cif`` subdirectory:

* `gemmi-read` - reads the CIF file from Python
* `gemmi-validate-fast` - only parses a file w/o copying any data
* `gemmi-validate` - parses and copies all the data into a DOM structure
* `cif_api` - runs `cif2_syncheck` from cif_api, as in a benchmark in
  [this paper](http://dx.doi.org/10.1107/S1600576715021883).
* `cif_api_fast` - the same, but with the `-f` option (does not create DOM)
* `cod-cifparse` - runs `cifparse`
  from [cod-tools](https://github.com/cod-developers/cod-tools)
* `iotbx-read` - calls `iotbx.cif.reader()` from cctbx/iotbx (Python)
* `pdbx` -
  [pdbx module](http://mmcif.wwpdb.org/docs/sw-examples/python/html/index.html)
  is a Python parser from RCSB PDB.


The benchmark was run using the `run.sh` script from this repository:

    for prog in read-cif/*; do ./run.sh $prog; done

Each combination of script/program and cif file was timed 10 times
and the fastest time was reported.
The benchmark was run on a Linux system, CPU i7-4790, 16GB RAM with
 12GB limit on the program memory (`ulimit -v 12582912`).
The libraries were compiled with GCC 5 with default options (-O2 or -O3),
or installed from binaries (iotbx).

### Run time (seconds)

|       program         | 4fxz | 1cjb | 3j3q  | r4v9psf |  CCD   |
| --------------------- | ---: | ---: | ----: | ------: | -----: |
| `gemmi-read`          | 0.02 | 0.03 |  2.80 |    2.73 |   2.90 |
| `gemmi-validate`      | 0.00 | 0.01 |  2.71 |    2.66 |   2.88 |
| `gemmi-validate-fast` | 0.00 | 0.00 |  1.33 |    1.16 |   1.14 |
| `cif_api`             | 2.25 | 4.78 |  ages |   ages  |        |
| `cif_api_fast`        | 0.01 | 0.02 |  5.99 |    4.36 |   5.90 |
| `cod-cifparse`        | 0.03 | 0.07 | 26.58 |   15.81 |  13.86 |
| `iotbx-read`          | 0.26 | 0.31 |  OOM  |   22.34 | 118.40 |
| `pdbx`                | 0.11 | 0.19 | 51.28 |   45.40 |  47.92 |

OOM = out-of-memory error

### Peak memory (MB)

|       program         | 4fxz | 1cjb  | 3j3q  | r4v9psf |  CCD  |
| --------------------- | ---: | ----: | ----: | ------: | ----: |
| `gemmi-read`          | 17.4 |  21.4 |  2287 |  2321   |  1726 |
| `gemmi-validate`      |  9.5 |  12.9 |  2279 |  2313   |  1717 |
| `gemmi-validate-fast` |  3.9 |   3.8 |   237 |   254   |   241 |
| `cif_api`             |  9.3 |   9.2 |   x   |  x      | x     |
| `cif_api_fast`        |  5.2 |   5.2 |     7 |     5   |     5 |
| `cod-cifparse`        |  8.8 |  15.7 |  3985 |  2835   |  3100 |
| `iotbx-read`          | 98.0 | 118.2 |  OOM  |  8768   |  9320 |
| `pdbx`                | 14.4 |  18.6 |  2895 |  1821   |  2353 |

Just for comparison:
* parsing [1cjb MMTF file](http://mmtf.rcsb.org/v1.0/full/1cjb.mmtf.gz)
  with Python parser takes 0.26s (47MB mem),
* parsing
  [1cjb mmJSON](https://pdbj.org/rest/downloadPDBfile?id=1CJB&format=mmjson-all)
  with Python built-in parser takes 0.03s (17MB).

And if you are interested in parsing small CIF files this benchmark
is more relevant: https://github.com/cod-developers/CIF-parsers

## Creating a structural model

Here we benchmark reading coordinate mmCIF files
and interpreting their content as a structural model,
which may involve building a model-chain-residue-atom hierarchy.

The scripts that are run are in the ``read-model`` subdirectory.
They happen to all be Python scripts:

* `gemmi-structure` - calls `gemmi.read_structure()` from Python.
  Internally, it first copies all the data into DOM structure, and then
  reads it to create a Model-Chain-Residue-Atom hierarchy (copying the data
  again).
* `biopython` - calls `MMCIFParser().get_structure()`
* `biopython-fast` - calls `FastMMCIFParser().get_structure()`
* `clipper-python` - calls `clipper.MMDBfile().read_file()`
* `iotbx-pdb` - calls `iotbx.pdb.input()`

These benchmarks can be run only with coordinate files.
Here I use only two of them: 1cjb.cif and 3j3q.cif:

    for prog in read-model/*; do ./run-one.sh $prog 1cjb.cif; done
    for prog in read-model/*; do ./run-one.sh $prog 3j3q.cif; done

|       program         | 1cjb | mem  | 3j3q  |  mem  |
| --------------------- | ---: | ---: | ----: | ----: |
| `gemmi-structure`     | 0.03 |  22  |   3.8 | 2288  |
| `biopython`           | 0.49 |  53  | 128.5 | 6655  |
| `biopython-fast`      | 0.26 |  55  |  45.8 | 7512  |
| `clipper-python`      | ERR  |      |  44.8 | 2353  |
| `iotbx-pdb`           | 0.40 | 110  |  ERR  |       |

The table reports elapsed time in seconds and peak memory in MB.
