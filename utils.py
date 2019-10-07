# encoding=utf-8
# created by Ge Zhang @ Sep 27, 2019
# contact zhangge9194@pku.edu.cn
#
# all kinds of common functions

import os
import json
from tqdm import tqdm
from extract_func import process_file
from config import nb_path
import re


def count_all_functions(out_path, notebooks=None):
    """
    extract all functions in target notebooks
    calculate the number of occurrences
    """
    if notebooks is None:
        notebooks = [f for f in os.listdir(nb_path) if f.endswith('.py')]
    print('len(notebooks): {}'.format(len(notebooks)))

    func_counter = {}
    error_files = []
    for f in tqdm(notebooks):
        try:
            funcs, linenos = process_file(os.path.join(nb_path, f))
            for f in funcs:
                if f not in func_counter:
                    func_counter[f] = 0
                func_counter[f] += 1
        except Exception as e:
            error_files.append(f)

    print('len(error_files): {}'.format(len(error_files)))
    with open(out_path, 'w') as fout:
        json.dump({"func_counter": func_counter,
                   "error_files": error_files}, fout, ensure_ascii=False, indent=2)


def split_func_name(func):
    """
    split function names
    eg. sklearn.metrics.pairwise.cosine_similarity -> [sklearn, metrics, pairwise, cosine, similarity]
    """
    new_str = ''
    for i, l in enumerate(func):
        if i > 0 and l.isupper() and func[i - 1].islower():
            new_str += '.'
        new_str += l
    return re.split('\.|_', new_str.lower())


if __name__ == '__main__':

    # with open('./py3_counter.txt', 'r') as f:
    #     error_files = json.load(f)["error_files"]
    # count_all_functions('./py2_counter.txt', error_files)
    with open('./py2_counter.txt', 'r') as f:
        data2 = json.load(f)
    with open('./py3_counter.txt', 'r') as f:
        data3 = json.load(f)
    error_files = data2["error_files"]
    func_counter = data2["func_counter"]
    for f in data3["func_counter"]:
        if f not in func_counter:
            func_counter[f] = data3["func_counter"][f]
        else:
            func_counter[f] += data3["func_counter"][f]
    with open('./func_counter.json', 'w') as fout:
        json.dump({"func_counter": func_counter,
                   "error_files": error_files}, fout, ensure_ascii=False, indent=2)
    # notebooks = [f for f in os.listdir(nb_path) if f.endswith('.py')]

    # count_all_functions('./py3_counter.txt', notebooks)
