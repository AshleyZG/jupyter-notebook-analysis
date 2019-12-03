# encoding=utf-8

import ast
import astunparse
import os
import pdb
import random
import re
from tqdm import tqdm
import argparse
import json


from config import toy_path, nb_path, toy_raw_graph_path, raw_graph_path
from graph_generator.graph import Graph, MetaGraph
from utils import is_decision_point, cut_cells_from_py

parser = argparse.ArgumentParser()

parser.add_argument("-out_path", type=str, required=True,
                    help='Where to save outputs')
parser.add_argument("-max_seq_length", type=int, default=150)
parser.add_argument("-max_n_graphs", type=int, help="max number of graphs")
parser.add_argument("--debug", action="store_true", help="debug mode")
args = parser.parse_args()


window = 2
lineno = 0
node_index = -1
nodes = []
unwanted_tokens = ['array', 'import']
target_linenos = {}
target_nodes = {}
linenos = []

with open('./file_funcs.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
# pdb.set_trace()


class Tree2Code(ast.NodeVisitor):
    '''
    detect target code lines
    '''

    def generic_visit(self, node):
        global lineno

        if 'lineno' in node.__dict__:
            if node.lineno > lineno:
                lineno = node.lineno
                lines = [l for l in astunparse.unparse(
                    node).split('\n') if l != '']
                if len(lines) == 1:

                    if lineno in linenos:
                        target_linenos[lineno] = node_index
                        target_nodes[lineno] = node
        ast.NodeVisitor.generic_visit(self, node)


visitor = Tree2Code()
counter = {}


def get_target_funcs(file, key_lib='', return_all=False):
    '''
    抽取一个 python file 中所有 target functions
    '''
    assert file.endswith('.py'), '{} is not a python file'.format(file)
    filename = file.split('/')[-1]
    # pdb.set_trace()
    assert filename in data, ("File {} cannot be parsed in python3.6".format(
        filename))
    # funcs, linenos = process_file(file)
    funcs = data[filename]["funcs"]
    linenos = data[filename]["linenos"]
    if return_all:
        return funcs, linenos
    target_funcs = [(func, lineno) for func, lineno in zip(
        funcs, linenos) if func.startswith(key_lib) and is_decision_point(func)]
    # try:
    if target_funcs:
        funcs, linenos = list(zip(*target_funcs))
    else:
        funcs = []
        linenos = []
    # except:
    #     pdb.set_trace()
    funcs = list(funcs)
    linenos = list(linenos)
    return funcs, linenos


def process_file(file, graph_obj=Graph):
    global target_linenos
    global target_nodes
    global lineno
    global linenos
    global node_index
    target_linenos = {}
    target_nodes = {}
    linenos = []
    lineno = 0
    node_index = -1

    funcs, linenos = get_target_funcs(file, key_lib='sklearn')
    l2f = {l: f for l, f in zip(linenos, funcs)}
    with open(file, 'r') as f:
        source_codes = f.read()
    tree = ast.parse(source_codes)

    for i, node in enumerate(tree.body):
        node_index = i
        visitor.visit(node)

    graphs = []
    for target_lineno, node_idx in target_linenos.items():
        graph = graph_obj([node for node in tree.body[max(node_idx - window, 0):node_idx +
                                                      window + 1] if not isinstance(node, ast.ImportFrom)], target_lineno, target_nodes[target_lineno], file, l2f[target_lineno])
        if len(graph) > args.max_seq_length:
            continue
        graphs.append(graph)

        graph.dump_into_file(args.out_path, merge=True)
    return graphs


def process_notebook_by_cell(file, graph_obj=MetaGraph):
    global target_linenos
    global target_nodes
    global lineno
    global linenos
    global node_index
    target_linenos = {}
    target_nodes = {}
    linenos = []
    lineno = 0
    node_index = -1

    funcs, linenos = get_target_funcs(file, return_all=True)
    cells = cut_cells_from_py(file)
    cells_len = [len(c.split('\n')) for c in cells]
    cells_func = []
    prev_len = 0
    for i, l in enumerate(cells_len):
        # pdb.set_trace()
        lines = [ll for ll in linenos if ll < prev_len + l and ll > prev_len]
        # pdb.set_trace()
        cells_func.append(funcs[:len(lines)])
        funcs = funcs[len(lines):]
        linenos = linenos[len(lines):]
        prev_len += l - 1
    prev_len = 0
    graphs = []
    for c, l, f in zip(cells, cells_len, cells_func):
        # root = ast.parse(c)
        # if root.body:
        #     graph = MetaGraph(root.body, prev_len,
        #                       root.body[0], file, 'none_func', funcs=f)
        #     if len(graph.nodes) <= 64:
        #         graphs.append(graph)
        #         graph.dump_into_file(args.out_path, merge=True)

        try:
            root = ast.parse(c)
            if root.body:
                graph = MetaGraph(root.body, prev_len,
                                  root.body[0], file, 'none_func', funcs=f)
                if len(graph.nodes) <= 64:
                    graphs.append(graph)
                    graph.dump_into_file(args.out_path, merge=True)
        except:
            pass
        prev_len += l - 1
        # pdb.set_trace()
    return graphs
    # raise NotImplementedError


if __name__ == '__main__':

    path = '/projects/bdata/jupyter/target'
    all_graphs = []
    error_files = []
    for file in tqdm(os.listdir(path)):

        try:
            graphs = process_notebook_by_cell(os.path.join(
                path, file), graph_obj=MetaGraph)
            all_graphs += graphs
        except Exception as e:
            # print(e)
            # print(file)
            error_files.append(file)

        if args.debug and len(all_graphs) > 10:
            break
        elif args.max_n_graphs and len(all_graphs) > args.max_n_graphs:
            break
        else:
            pass

    print('[Info] get {} graphs'.format(len(all_graphs)))

    with open('error.out', 'w') as f:
        f.write('\n'.join(error_files))
