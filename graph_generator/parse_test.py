# coding=utf-8
# created Jan 12 2020, by Ge Zhang
# parse test annotated notebooks

import os
import json
import ast
import pdb
import itertools
from extract_func import process_file


def is_python_line(line):
    line = line.strip()
    if line.startswith('!'):
        return False
    elif line.startswith('%'):
        return False
    return True


path = '/projects/bdata/jupyter/annotation/ge'

files = [f for f in os.listdir(path) if f.endswith('.json')]
files = ['nb_1089313.json', 'nb_1024739.json', 'nb_1058499.json', 'nb_1161031.json', 'nb_1105414.json', 'nb_1189833.json', 'nb_1031433.json', 'nb_1242794.json', 'nb_1025815.json', 'nb_1236355.json', 'nb_1004385.json', 'nb_1163520.json', 'nb_1240128.json', 'nb_1245037.json', 'nb_1149480.json', 'nb_1223629.json', 'nb_1234699.json', 'nb_1203216.json', 'nb_1226996.json', 'nb_1234234.json', 'nb_1159388.json', 'nb_1090484.json',
         'nb_1221697.json', 'nb_1138647.json', 'nb_1116374.json', 'nb_1068488.json', 'nb_1026834.json', 'nb_1034447.json', 'nb_1202205.json', 'nb_1138666.json', 'nb_1005070.json', 'nb_1043186.json', 'nb_1002722.json', 'nb_1183943.json', 'nb_1122022.json', 'nb_1227519.json', 'nb_1068026.json', 'nb_1183781.json', 'nb_1109134.json', 'nb_1222945.json', 'nb_1183716.json', 'nb_1108440.json', 'nb_1221634.json', 'nb_1090152.json']
error_files = []
all_cells = []
for file in files:
    with open(os.path.join(path, file), 'r') as f:
        cells = json.load(f)

    cells = [c for c in cells if c["cell_type"] == 'code']
    code_lines = list(itertools.chain.from_iterable(
        [c["source"] for c in cells]))
    code_lines = [l for l in code_lines if is_python_line(l)]
    source = '# In[]:\n'.join(code_lines)

    try:
        # root = ast.parse(source)
        funcs, linenos = process_file(os.path.join(path, file), content=source)
        py_cells = source.split('# In[]:\n')
        prev_len = 0
        cell_funcs = []
        for cell in py_cells:

            cell_len = len(cell.split('\n'))

            temp_func = [f for f, l in zip(
                funcs, linenos) if l <= prev_len + cell_len and l > prev_len]
            # pdb.set_trace()
            cell_funcs.append(temp_func)
            prev_len += cell_len
        # for cf, pc in zip(cell_funcs, py_cells):
        counter = 0
        for c in cells:
            c["funcs"] = []
            for l in c["source"]:
                if not is_python_line(l):
                    continue
                c["funcs"] += cell_funcs[counter]
                counter += 1
            all_cells.append(c)

    except Exception as e:
        # print(e)
        # pdb.set_trace()
        error_files.append(file)

with open('./temp_1_13.txt','a') as fout:
	for c in all_cells:
		fout.write(json.dumps(c))
		fout.write('\n')
# print(error_files)
# print(len(error_files))
