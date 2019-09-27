# encoding=utf-8
# Created by Ge Zhang @ 2019
#
# Used for preprocessing
# filter files that use certain libs
# to see key libraries: **key_libs** in **config.py**
import os
import json
import random
import re
import shutil
from tqdm import tqdm

from pre_load import key_methods
from config import key_libs


def is_data_science_py(file):
    # key_libs = ['statsmodels', 'gensim',
    #             'keras', 'sklearn', 'xgboost', 'scipy']
    with open(file, 'r') as f:
        source_codes = f.read()
    tokens = source_codes.split()
    if any([lib in tokens for lib in key_libs]):
        return True
    else:
        return False


def select_data_science_py(dir_path, aim_path, max_num_files=None):
    wanted = []
    source_files = os.listdir(dir_path)
    if not os.path.exists(aim_path):
        os.mkdir(aim_path)
    if max_num_files is not None:
        source_files = source_files[:max_num_files]
    for file in tqdm(source_files):
        if os.path.exists(os.path.join(aim_path, file)):
            continue
        if not file.endswith('.py'):
            continue

        if is_data_science_py(os.path.join(dir_path, file)):
            wanted.append(file)

    print(len(wanted))
    for file in tqdm(wanted):

        shutil.copy(os.path.join(dir_path, file), os.path.join(aim_path, file))


if __name__ == '__main__':

    select_data_science_py(
        '/home/gezhang/_6_1', '/home/gezhang/data/jupyter/target')
