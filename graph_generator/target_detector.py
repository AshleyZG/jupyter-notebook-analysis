import ast
import astunparse
import os
import pdb
import random
import re
from tqdm import tqdm


# from config import *
from config import toy_path, nb_path, toy_raw_graph_path, raw_graph_path
from graph_generator.graph import Graph
from graph_generator.generator import get_target_funcs

window = 5
lineno = 0
node_index = -1
nodes = []
unwanted_tokens = ['array', 'import']
target_linenos = {}
target_nodes = {}
linenos = []


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
                    # is_target = is_target_node(node)
                    # if is_target:
                    if lineno in linenos:
                        target_linenos[lineno] = node_index
                        target_nodes[lineno] = node
        ast.NodeVisitor.generic_visit(self, node)


visitor = Tree2Code()


def process_file(file):
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

    funcs, linenos = get_target_funcs(file)
    with open(file, 'r') as f:
        source_codes = f.read()
    tree = ast.parse(source_codes)

    for i, node in enumerate(tree.body):
        node_index = i
        visitor.visit(node)

    graphs = []
    for target_lineno, node_idx in target_linenos.items():
        graph = Graph(tree.body[max(node_idx - window - 1, 0):node_idx +
                                window + 1], target_lineno, target_nodes[target_lineno])
        graphs.append(graph)
        graph.dump_into_file(os.path.join(
            raw_graph_path, '{}${}.json'.format(target_lineno, file.split('/')[-1])))
    return graphs


def temp_process_file(file):
    with open(file, 'r') as f:
        source_codes = f.read()
    tree = ast.parse(source_codes)
    for i, node in enumerate(tree.body):
        graph = Graph(tree.body[max(i - window - 1, 0):i +
                                window + 1], node.lineno, node)
        graph.dump_into_file(os.path.join(
            './temp_graphs_no_mark', '{}${}.json'.format(i, file.split('/')[-1])))


def temp_enter():
    # file = random.choice(os.listdir(toy_path))
    file = '/home/gezhang/data/jupyter/toy/nb_356071.py'
    return temp_process_file(file)


if __name__ == '__main__':
    print('hello')
    # all_graphs = []
    # error_files = []
    # for file in tqdm(os.listdir(nb_path)):
    #     try:
    #         graphs = process_file(os.path.join(nb_path, file))
    #         all_graphs += graphs
    #     except Exception as e:
    #         error_files.append(file)
    # print('[Info] get {} graphs'.format(len(all_graphs)))
    # # all_functions = sorted(list(set(all_functions)))
    # # print('[Info] {} different functions'.format(len(all_functions)))
