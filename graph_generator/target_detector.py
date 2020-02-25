# encoding=utf-8
# created by Ge Zhang, 2019
#
# main file
# generate graphs from python scripts

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
from graph import Graph, MetaGraph
from utils import is_decision_point, cut_cells_from_py, ipynb2py, get_cell_labels_from_html
from nbconvert import PythonExporter, HTMLExporter
from extract_func import process_file
from datetime import date

DATE = date.today().strftime("%m%d_%Y")


py_exporter = PythonExporter()


parser = argparse.ArgumentParser()
parser.add_argument("-input_path", type=str,
                    required=True, help="Path to input py/ipynb")
parser.add_argument("-out_path", type=str, required=True,
                    help='Where to save outputs')
parser.add_argument("-max_seq_length", type=int, default=150)
parser.add_argument("-max_n_graphs", type=int, help="max number of graphs")
parser.add_argument("--debug", action="store_true", help="debug mode")
parser.add_argument("--test", action="store_true",
                    help="generate graphs for evaluation")
args = parser.parse_args()


window = 2
lineno = 0
node_index = -1
nodes = []
unwanted_tokens = ['array', 'import']
target_linenos = {}
target_nodes = {}
linenos = []

# with open('./file_funcs.json', 'r', encoding='utf-8') as f:
with open('./file_funcs.json', 'r') as f:
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


def get_target_funcs(file, key_lib='', return_all=False, python2=False):
    '''
    抽取一个 python file 中所有 target functions
    '''
    assert file.endswith('.py'), '{} is not a python file'.format(file)
    filename = file.split('/')[-1]
    # pdb.set_trace()
    if not python2:
        assert filename in data, ("File {} cannot be parsed in python3.6".format(
            filename))
        # funcs, linenos = process_file(file)
        funcs = data[filename]["funcs"]
        linenos = data[filename]["linenos"]
    else:
        funcs, linenos = process_file(file)
        # raise NotImplementedError
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


def process_file_2(file, graph_obj=Graph):
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

    funcs, linenos = get_target_funcs(file, return_all=True, python2=True)
    # pdb.set_trace()
    cells = cut_cells_from_py(file)
    cells_len = [len(c.split('\n')) for c in cells]
    cells_func = []
    prev_len = 0
    for i, l in enumerate(cells_len):

        lines = [ll for ll in linenos if ll < prev_len + l and ll > prev_len]

        cells_func.append(funcs[:len(lines)])
        funcs = funcs[len(lines):]
        linenos = linenos[len(lines):]
        prev_len += l - 1
    prev_len = 0
    graphs = []
    for c, l, f in zip(cells, cells_len, cells_func):
        root = ast.parse(c)

        if root.body:
            graph = MetaGraph(root.body, prev_len,
                              root.body[0], file, 'none_func', funcs=f)
            # if len(graph.nodes) <= 64:
            graphs.append(graph)
            # graph.dump_into_file(args.out_path, merge=True)
        # try:
        #   root = ast.parse(c)
        #   if root.body:
        #     graph = MetaGraph(root.body, prev_len,
        #                       root.body[0], file, 'none_func', funcs=f)
        #     # if len(graph.nodes) <= 64:
        #     graphs.append(graph)
        #     graph.dump_into_file(args.out_path, merge=True)
        # except:
        #   pass
        prev_len += l - 1

    return graphs


def process_test_notebook_by_cell(file, graph_obj=MetaGraph):
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

    # load labeled stages
    nb_id = file.split('/')[-1].split('.')[0]
    with open(os.path.join('./templates', '{}.html'.format(nb_id)), 'r') as f:
        html_source = f.read()
    stages = get_cell_labels_from_html(html_source)
    stages = [s for s in stages if s != '0']
    if file.endswith('.ipynb'):
        file = ipynb2py(file)

    funcs, linenos = process_file(file)

    cells = cut_cells_from_py(file)
    cells_len = [len(c.split('\n')) for c in cells]

    cells_func = []

    prev_len = 0
    for i, l in enumerate(cells_len):

        lines = [ll for ll in linenos if ll < prev_len + l and ll > prev_len]

        cells_func.append(funcs[:len(lines)])
        funcs = funcs[len(lines):]
        linenos = linenos[len(lines):]
        prev_len += l - 1

    cells_func = [cells_func[i]
                  for i, c in enumerate(cells) if c.strip() and ast.parse(c).body]
    cells = [c for c in cells if c.strip() and ast.parse(c).body]
    cells_len = [len(c.split('\n')) for c in cells]

    assert len(cells) == len(stages), "{}, cell split error".format(nb_id)
    if len(cells) == len(stages) + 1:
        cells = cells[1:]
        cells_len = cells_len[1:]
    prev_len = 0
    graphs = []
    for c, l, s, f in zip(cells, cells_len, stages, cells_func):
        root = ast.parse(c)
        if root.body:
            graph = MetaGraph(root.body, prev_len,
                              root.body[0], file, 'none_func', stage=s, funcs=f)
            # pdb.set_trace()
            graphs.append(graph)
            graph.dump_into_file(args.out_path, merge=True)

        prev_len += l - 1

    return graphs


def generate_graphs_from_files(path, files, process_method):
    all_graphs = []
    error_files = []
    for file in tqdm(files):
        # graphs = process_method(os.path.join(
        #     path, file), graph_obj=MetaGraph)
        # # pdb.set_trace()
        # all_graphs += graphs
        try:
            graphs = process_method(os.path.join(
                path, file), graph_obj=MetaGraph)
            # pdb.set_trace()
            all_graphs += graphs
        except Exception as e:
            # print(file, e)
            # print(file)
            error_files.append(file)

        if args.debug and len(all_graphs) > 10:
            break
        elif args.max_n_graphs and len(all_graphs) > args.max_n_graphs:
            break
        else:
            pass
    with open(args.out_path, 'a') as fout:

        for g in all_graphs:
            fout.write(json.dumps(g.get_metadata()))
            fout.write('\n')
        # raise NotImplementedError
    # raise NotImplementedError
    return all_graphs, error_files


if __name__ == '__main__':

    path = args.input_path
    if args.test:
        files = ['nb_1002722.py',
                 'nb_1183716.py',
                 'nb_1089165.py',
                 'nb_1090484.py',
                 'nb_1034447.py',
                 'nb_1234699.py',
                 'nb_1089313.py',
                 'nb_1005070.py',
                 'nb_1221634.py',
                 'nb_1183943.py',
                 'nb_1122022.py',
                 'nb_1226996.py',
                 'nb_1138666.py',
                 'nb_1245037.py',
                 'nb_1022912.py',
                 'nb_1116374.py',
                 'nb_1068488.py',
                 'nb_1163520.py',
                 'nb_1051445.py',
                 'nb_1026834.py',
                 'nb_1202205.py',
                 'nb_1005207.py',
                 'nb_1149480.py',
                 'nb_1058499.py',
                 'nb_1215918.py',
                 'nb_1236355.py',
                 'nb_1221697.py',
                 'nb_1240128.py',
                 'nb_1223629.py',
                 'nb_1024739.py',
                 'nb_1031433.py',
                 'nb_1109134.py',
                 'nb_1203216.py',
                 'nb_1242794.py',
                 'nb_1227519.py',
                 'nb_1161031.py',
                 'nb_1183781.py',
                 'nb_1222945.py',
                 'nb_1234234.py',
                 'nb_1159388.py',
                 'nb_1090152.py',
                 'nb_1138647.py',
                 'nb_1043186.py',
                 'nb_1189833.py',
                 'nb_1068026.py',
                 'nb_1105414.py']
    else:
        files = os.listdir(path)

        with open('./files_2_2.txt', 'r') as f:
            files = f.read().split('\n')
        # files = files[:1000]
        files = files[1000:65103]
    all_graphs, error_files = generate_graphs_from_files(
        path, files, process_test_notebook_by_cell if args.test else process_notebook_by_cell)

    print('[Info] get {} graphs'.format(len(all_graphs)))

    with open('error_{}.out'.format(DATE), 'w') as f:
        f.write('\n'.join(error_files))
