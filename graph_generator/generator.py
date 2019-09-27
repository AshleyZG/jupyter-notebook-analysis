import random
import os
import pdb
import json
from tqdm import tqdm

from extract_func import process_file
from config import toy_path, key_methods_path, nb_path, key_libs
from pre_load import key_methods

with open('./keras/keras.optimizers_100.txt', 'r') as f:
    # nobs = json.loads()
    topk_funcs = json.load(f).keys()

is_dp = {}
with open('./nobs_similars_100.txt', 'r') as f:
    for l in f:
        data = json.loads(l)
        is_dp[data['function']] = data['is_decision_point']


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


def new_is_selected_func(func):
    '''
    判断 func 是否以 'statsmodels', 'gensim', 'keras', 'sklearn', 'xgboost' 开头
    '''
    # key_libs = ['statsmodels', 'gensim', 'keras', 'sklearn', 'xgboost']
    if func.split('.')[0] in key_libs:
        return True
    else:
        return False


def func_in_top_100(func):
    if func in topk_funcs:
        return True
    else:
        return False
    # raise NotImplementedError

# def topk_func_startswith(func, suffix, )


def get_target_funcs(file):
    '''
    抽取一个 python file 中所有 target functions
    '''
    assert file.endswith('.py'), '{} is not a python file'.format(file)

    funcs, linenos = process_file(file)

    target_funcs = [(func, lineno) for func, lineno in zip(
        funcs, linenos) if new_is_selected_func(func)]
    funcs, linenos = list(zip(*target_funcs))
    funcs = list(funcs)
    linenos = list(linenos)
    return funcs, linenos


if __name__ == '__main__':
    # assert False
    path = '/home/gezhang/data/jupyter/target'
    all_functions = []
    error_files = []
    for file in tqdm(os.listdir(path)):
        try:
            funcs, _ = get_target_funcs(os.path.join(path, file))
            all_functions += funcs
        except Exception as e:
            error_files.append(file)
    print('[Info] get {} related functions'.format(len(all_functions)))
    all_functions = sorted(list(set(all_functions)))
    print('[Info] {} different functions'.format(len(all_functions)))
    pdb.set_trace()
