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
