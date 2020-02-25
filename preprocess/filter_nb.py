# coding=utf-8
# created Jan 12, 2020 by Ge Zhang

# filter notebooks for train (python2)


import json
import pdb
from tqdm import tqdm
import os

graphs = []
files = []
with open('./graphs/temp_cell_with_func.txt', 'r') as f:
    for l in tqdm(f):
        g = json.loads(l)
        graphs.append(g)
        # if g['file'] not in files:
        #     files.append(g['file'])
        # pdb.set_trace()
files = [g['file'].split('/')[-1] for g in graphs]
files = list(set(files))

all_files = set(os.listdir('/projects/bdata/jupyter/target'))
files = set(files)
# pdb.set_trace()
new_files = all_files - files
print(len(new_files))
# new_files = list(new_files)
# new_files = [f for f in all_files if f not in files]
# new_files = []
# for f in tqdm(all_files):
#     if f not in files:
#         new_files.append(f)
print(len(new_files))
# print(new_files)
with open('./files_1_12.txt', 'w') as fout:
    fout.write('\n'.join(new_files))
