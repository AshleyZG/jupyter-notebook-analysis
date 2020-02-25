# coding=utf-8
# created Jan 23, 2020 by Ge Zhang
#
# generate academic graphs from cells
# './aca_cells.txt'

import os
import json
from graph import MetaGraph
import ast
import pdb
from tqdm import tqdm


def is_python_line(line):
    if line.strip().startswith('%'):
        return False
    if line.strip() == '%matplotlib inline':
        # print()
        return False

    if line.strip() == '% matplotlib inline':
        return False
    if line.strip() == '%load_ext autoreload':
        return False
    if line.strip() == '%autoreload 2':
        return False
    if line.strip() == '%pylab inline':
        return False
    if line.strip().startswith('!'):
        return False
    return True


cells = []
with open('./error_cells.txt', 'r') as f:
    for l in f:
        cells.append(json.loads(l))

graphs = []
error_cells = []
for c in tqdm(cells):

    try:
        source = c["code"]
        source = [l for l in source if is_python_line(l)]
        root = ast.parse('\n'.join(source))
        if root.body:
            graph = MetaGraph(root.body, c["target_lineno"],
                              root.body[0], c["file"], 'none_func')
            graph.dump_into_file('./graphs/aca_graphs.txt', merge=True)
        graphs.append(graph)
    except:
        error_cells.append(c)
        # pass

with open('./error_cells.txt', 'w') as fout:
    for c in error_cells:
        fout.write(json.dumps(c))
        fout.write('\n')


print(len(graphs))
