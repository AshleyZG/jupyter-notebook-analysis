'functions to preprocess data, also a try of KMeans'

from config import *

import os
import json
import random
import re
import shutil


from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans


def extract_code(ipynb_file):
    'extract codes from notebook'
    '''
    ipynb_file: str
    cell_sources: List[str]
    '''
    with open(ipynb_file, 'r') as f:
        notebook = json.load(f)

    cell_sources = []
    if 'cells' not in notebook:
        return cell_sources
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':

            cell_sources += cell['source']
    return cell_sources


def clean_code(line):
    'convert a line of code to a list of tokens'
    '''
    line: str
    '''
    tokens = re.compile(r'[.():\[\]{}+-/*=><\\]+')
    inside_quote = re.compile(r'\'.*?\'')
    inside_double_quote = re.compile(r'\".*?\"')

    line = re.sub(tokens, ' ', line)
    line = re.sub(inside_quote, '', line)
    line = re.sub(inside_double_quote, '', line)

    return line


def filter_import_code(source_codes):
    'filter import codes'
    '''
    source_codes: List[str]
    return: List[str]
    '''
    return [code for code in source_codes if 'import' in code]


def import_in_file(path, ipynb_file):
    'decide whether notebook has import codes'
    '''
    ipynb_file: str
    return: bool
    '''
    return filter_import_code(extract_code(os.path.join(path, ipynb_file))) != []


def copy_files(src_path, dst_path, files):
    'copy files in src_path to dst_path'
    '''
    src_path: str
    dst_path: str
    files: List[str]
    '''
    for file in files:
        shutil.copy(os.path.join(src_path, file), os.path.join(dst_path, file))


def extract_library(code):
    'print libraries used in code'
    '''
    code: str
    '''
    tokens = re.split(r'[\s,]', code.strip())
    if code[:6] == 'import' or code[:4] == 'from':
        if 'from' in tokens:
            print(code)
            print(tokens[1], tokens[3])
        else:
            print(code)
            print(tokens[1:])


def is_data_science_nb(path, ipynb_file):
    'decide whether notebook is for data analysis'
    '''
    path: str
    ipynb_file: str
    return: bool
    '''
    sources = extract_code(os.path.join(path, ipynb_file))
    for code in sources:
        for lib in libraries:
            if lib in code:
                return True
    return False


def remove_files(path, files):
    'delete files in directory path'
    '''
    path: str
    files: List[str]
    '''
    for file in files:
        os.remove(os.path.join(path, file))


def filter_files(path, files):
    'filter files in path that use data analysis libraries'
    '''
    path: str
    files: List[str]
    selected: List[str]
    deleted: List[str]
    '''
    selected = []
    deleted = []
    for file in files:
        try:
            if is_data_science_nb(path, file):
                selected.append(file)
            else:
                deleted.append(file)
        except:
            pass
    return selected, deleted


if __name__ == '__main__':

    files = [f for f in os.listdir(nb_path) if f.endswith('.ipynb')]
    file = rancom.choice(files)
    print(is_data_science_nb(nb_path, file))
