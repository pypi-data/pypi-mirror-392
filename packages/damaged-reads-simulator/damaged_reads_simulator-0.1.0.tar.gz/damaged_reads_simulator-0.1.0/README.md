# reads_simulator
Simulates NGS sequenced reads

## Installation
```
python3 -m venv readsim_env
source readsim_env/bin/activate

pip install fast_string_replace numpy
```
for prototyping with marimo:
```
pip install marimo matplotlib seaborn
```

## Usage
```
python ../generate_reference_and_reads.py <parameters.info>
```

where parameters.info file should be as follows.
```
# SYNTAX IS IMPORTANT
# LInes starting with # are comments
# name of the parameter: value
# : not = | where True/False first letter is uppercase.
random seed: 402

# GENOME SIMULATION PARAMETERS
reference file path: None
generate reference: True
GC percentage: 40
length of contigs: 1000000,10000,50000,200000 

# READS SIMULATION PARAMETERS
number of reads: 100000
read_length: 76
insert length: 100
insert length variations: 35
type of library: FFPE

# METHYLATION PARAMETERS
methylation library: False
percent methylation: 96

# PREFIX TO BE USED IN LOG AND OUTPUT FILES
prefix: ffpe_nometh
```
The above should be modified to your needs.
