# coding=utf-8
# created by Ge Zhang, 2019
# contact: zhangge9194@pku.edu.cn
#
# filter notebooks by libraries


import os
import json
from tqdm import tqdm
# from config import key_libs
key_libs = ['statsmodels', 'gensim', 'keras',
            'sklearn', 'xgboost', 'scipy']

# key_libs = ['pandas']
path = '/projects/bdata/jupyter/_7_1'
with open('./py_3_good_nb_filter3_12_11.txt', 'r') as f:
    py = f.read().split()


def is_good_nb(content):
    # filter by number of cells
    if len(content["cells"]) < 2:
        return False
    if len([c for c in content["cells"] if c["cell_type"] == 'code']) < 1:
        return False
    # filter by line numbers and key lib
    n_lines = 0
    key = False
    for c in content["cells"]:
        if c["cell_type"] == 'markdown':
            continue
        source = '\n'.join(c["source"])
        n_lines += len([l for l in source.split('\n')
                        if l and not l.startswith(('#', '\''))])
        tokens = source.split()
        if not key and any([lib in tokens for lib in key_libs]):
            key = True
    return n_lines >= 10 and key


py_3_good_nb = []
err_files = []
for nb in tqdm(py):
    try:
        with open(os.path.join(path, nb), 'r', encoding='utf-8') as f:
            content = json.load(f)
        # print('___')
        if is_good_nb(content):
            py_3_good_nb.append(nb)
    except Exception as e:
        print(e)
        err_files.append(nb)
with open('./py_3_good_nb_filter4_12_11.txt', 'w') as fout:
    fout.write('\n'.join(py_3_good_nb))
with open('./err_files_py_3_good_nb_filter4_12_11.txt', 'w') as fout:
    fout.write('\n'.join(err_files))
print(len(py_3_good_nb))
print(len(err_files))
