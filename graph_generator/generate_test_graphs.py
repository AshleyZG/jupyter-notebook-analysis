# coding=utf-8
# created Jan 25,2020 by Ge Zhang

# generate test graphs

import json
import os
from graph import MetaGraph
import pdb
import ast

graphs = []
with open('./graphs/python2_test_graphs_1_26.txt', 'r') as f:
    for l in f:
        graphs.append(json.loads(l))


error_graphs = []

for i, g in enumerate(graphs):
    try:
        root = ast.parse(g["context"])
        file = g["file"]
        funcs = g["funcs"]
        # pdb.set_trace()
        graph = MetaGraph(root.body, g["position"],
                          root.body[0], file, 'none_func', stage=g["stage"], funcs=funcs, id_=i, annotation=g["annotation"], header="", neighbor_cells=[-1])
        graph.dump_into_file(
            "./graphs/python2_test_graphs_md_1_26.txt", merge=True)
    except Exception as e:
        # print (e)
        # print(g)
        # pdb.set_trace()
        error_graphs.append(g)

print(len(error_graphs))
