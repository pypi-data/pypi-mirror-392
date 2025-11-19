#!/usr/bin/env bash


tasmanian_output_csv=$1
parsed_counts=$(echo $1 | sed 's/csv/parsed.csv/')
parsed_normed=$(echo $1 | sed 's/csv/parsed_norm.csv/')

awk -F, '
{
    printf "%s,%s",$1,$2; 
    for (i=35;i<51;i++) {printf ",%s",$i}; 
    print ""
}' ${tasmanian_output_csv} > ${parsed_counts}


export parsed_counts
export parsed_normed

python3 <<EOF
import pandas as pd
from itertools import product
import os

d = pd.read_csv(os.environ.get('parsed_counts'))

b = ['a','t','c','g']

for j in b:
    d.loc[:, j+'_tot'] = d.loc[:, ['N'+j+'_'+i for i in b]].sum(axis=1)

for combs in product(b,b):
    c = 'N' + combs[0] + "_" + combs[1]

    d.loc[:, 'norm_' + combs[0] + "_" + combs[1] ] = d.loc[:, c] / d.loc[:, combs[0] + "_tot"] 

d.loc[:, ['read', 'position'] + [i for i in d.columns if i[:4] == 'norm']].to_csv(os.environ.get('parsed_normed'), index=False)
EOF
