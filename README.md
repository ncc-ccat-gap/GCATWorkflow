[![Build Status](https://api.travis-ci.com/ncc-ccat-gap/GCATWorkflow.svg?branch=master)](https://travis-ci.com/github/ncc-ccat-gap/GCATWorkflow)
![Python](https://img.shields.io/badge/python-3.6%20%7C%203.7-blue.svg)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

G-CAT Workflow
===============
G-CAT Workflow, a cancer genome and RNA sequencing data analysis pipeline, efficiently detects of genomic variants and transcriptomic changes. Users can run G-CAT Workflow with ease of use in the HGC supercomputer and also can run it in other high performance computers.

## Manual
https://github.com/ncc-ccat-gap/GCATWorkflow

For developers, https://github.com/ncc-ccat-gap/GCATWorkflow/wiki

## Setup

0. Precondition

Make DRMAA and singularity available beforehand.

1. Install

```
git clone https://github.com/ncc-ccat-gap/GCATWorkflow.git
cd GCATWorkflow
python setup.py install
```

2. Pull container images

```
singularity pull docker://genomon/bwa_alignment:0.2.0
```

3. Edit config file

Edit `image` options, to pulled `.simg`.  
And edit pathes of reference files.
```
vi ./tests/dna_gcat.cfg
```

4. Edit sample.csv

Edit pathes of sequence files.
```
vi ./tests/dna_sample.csv
```

## How to use

1. Configure

```
gcat_workflow dna ./tests/dna_sample.csv ${output_dir} ./tests/dna_gcat.cfg
```

2. `snakemake`
```
cd ${output_dir}
snakemake
```

case, dry-run
```
snakemake -n
```

case, re-run (force all)
```
snakemake --forceall
```

case, with dot
```
snakemake --forceall --dag | dot -Tpng > dag.png
```

![](./doc/dag.png)
