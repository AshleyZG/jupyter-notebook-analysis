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
# import urllib.request
from nbconvert import PythonExporter, HTMLExporter
import pdb
from bs4 import BeautifulSoup

py_exporter = PythonExporter()


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


def download_from_url(url, save_dir=""):
    filename = url.split('/')[-1]
    urllib.request.urlretrieve(url, os.path.join(save_dir, filename))
    return filename
    # raise NotImplementedError


def cut_cells_from_py(filename):
    # with open(filename, 'r', encoding='utf-8') as f:
    with open(filename, 'r') as f:
        sources = f.read()
    return re.split(r"# In\[[\s0-9]+\]:", sources)


def cut_cells_from_py_source(sources):
    return re.split(r"# In\[[\s0-9]+\]:", sources)


def ipynb2py(filename):
    py_source = py_exporter.from_file(filename)[0]
    py_filename = filename.replace('.ipynb', '.py')
    with open(py_filename, 'w') as fout:
        fout.write(py_source)
    return py_filename


def get_cell_labels_from_html(html_source):
    soup = BeautifulSoup(html_source)
    cells = soup.find_all("div", class_="inner_cell")
    stages = []
    for cell in cells:
        labeled_option = cell.find('option', {'selected': True})
        # stage = labeled_option["value"]
        stages.append(labeled_option["value"])
        # pdb.set_trace()
    return stages

    # raise NotImplementedError


if __name__ == '__main__':
    # print(DECISION_POINTS)
    py_source = py_exporter.from_file(
        '/projects/bdata/jupyter/_7_1/nb_1166597.ipynb')[0]
    cells = cut_cells_from_py_source(py_source)
    pdb.set_trace()
    cells = cut_cells_from_py('/projects/bdata/jupyter/_7_1/nb_1166597.ipynb')
