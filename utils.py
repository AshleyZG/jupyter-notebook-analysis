# encoding=utf-8
# created by Ge Zhang @ Sep 27, 2019
# contact zhangge9194@pku.edu.cn
#
# all kinds of common functions

import os
import json
from tqdm import tqdm
from extract_func import process_file
from config import nb_path, key_libs
import re

DECISION_POINTS = {}

for lib in key_libs:
    with open('/projects/bdata/jupyter/decision_points/{}.txt'.format(lib), 'r') as f:
        DECISION_POINTS[lib] = [l for l in f.read().split('\n') if l]


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


def is_number(s):
    try:
        float(s)
        return True
    except:
        return False


def split_func_name(func):
    """
    split function names
    eg. sklearn.metrics.pairwise.cosine_similarity -> [sklearn, metrics, pairwise, cosine, similarity]
    """
    new_str = ''
    for i, l in enumerate(func):
        if i > 0 and l.isupper() and func[i - 1].islower():
            new_str += '.'
        elif i > 0 and i < len(func) - 1 and l.isupper() and func[i - 1].isupper() and func[i + 1].islower():
            new_str += '.'
        elif i > 0 and l.isdigit() and func[i - 1].isalpha():
            new_str += '.'
        elif i < len(func) - 1 and l.isalpha() and func[i - 1].isdigit():
            new_str += '.'
        else:
            pass
        new_str += l
    return re.split('\.|_', new_str.lower())


def is_decision_point(func):
    tokens = (func + '.').split('.')
    if tokens[0] not in key_libs:
        return False
    lib = tokens[0]
    if func in DECISION_POINTS[lib]:
        return True
    return False


if __name__ == '__main__':
    print(DECISION_POINTS)
