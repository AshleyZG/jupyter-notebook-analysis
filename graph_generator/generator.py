import random
import os
import pdb
import json
from tqdm import tqdm

from extract_func import process_file
from config import toy_path, key_methods_path, nb_path
from pre_load import key_methods


def is_selected_func(func):
    '''
    判断 func 是否是 target function
    '''
    if func.split('.')[0] not in key_methods:
        return False

    if func.split('.')[1] in key_methods[func.split('.')[0]]:
        return True
    if any([func.startswith(target_func) for target_func in key_methods[func.split('.')[0]]]):
        return True
    return False


def get_target_funcs(file):
    '''
    抽取一个 python file 中所有 target functions
    '''
    assert file.endswith('.py'), '{} is not a python file'.format(file)
    # print('[Info] processing {}'.format(file))
    funcs, linenos = process_file(file)
    # target_funcs = [func, lineno for func, lineno in zip(funcs, linenos)]
    target_funcs = [(func, lineno) for func, lineno in zip(
        funcs, linenos) if is_selected_func(func)]
    funcs, linenos = list(zip(*target_funcs))
    funcs = list(funcs)
    linenos = list(linenos)
    return funcs, linenos


def temp_enter():
    file = random.choice(os.listdir(toy_path))
    return get_target_funcs(os.path.join(toy_path, file))


if __name__ == '__main__':
    assert False
    all_functions = []
    error_files = []
    for file in tqdm(os.listdir(nb_path)):
        try:
            funcs = get_target_funcs(os.path.join(nb_path, file))
            all_functions += funcs
        except Exception as e:
            error_files.append(file)
    print('[Info] get {} related functions'.format(len(all_functions)))
    all_functions = sorted(list(set(all_functions)))
    print('[Info] {} different functions'.format(len(all_functions)))
