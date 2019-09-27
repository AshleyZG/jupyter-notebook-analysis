import ast
import astunparse
import os
import pdb
import random
import re
from tqdm import tqdm
import argparse


from config import toy_path, nb_path, toy_raw_graph_path, raw_graph_path
from graph_generator.graph import Graph
from graph_generator.generator import get_target_funcs, topk_funcs


parser = argparse.ArgumentParser()

parser.add_argument("-out_path", type=str, required=True,
                    help='Where to save outputs')
parser.add_argument("-max_seq_length", type=int, default=150)
parser.add_argument("-max_number", default=None, type=int,
                    help='Maximum number of graphs per function')
args = parser.parse_args()


window = 1
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

                    if lineno in linenos:
                        target_linenos[lineno] = node_index
                        target_nodes[lineno] = node
        ast.NodeVisitor.generic_visit(self, node)


visitor = Tree2Code()
counter = {}


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
    l2f = {l: f for l, f in zip(linenos, funcs)}
    with open(file, 'r') as f:
        source_codes = f.read()
    tree = ast.parse(source_codes)

    for i, node in enumerate(tree.body):
        node_index = i
        visitor.visit(node)

    graphs = []
    # pdb.set_trace()
    for target_lineno, node_idx in target_linenos.items():
        # if l2f[target_lineno] not in counter:
        #     counter[l2f[target_lineno]] = 0
        # if args.max_number and counter[l2f[target_lineno]] > args.max_number:
        #     continue
        # counter[l2f[target_lineno]] += 1
        graph = Graph(tree.body[max(node_idx - window - 1, 0):node_idx +
                                window + 1], target_lineno, target_nodes[target_lineno], file, single_token=False, only_func=True, target_func=l2f[target_lineno])
        # =======Temp=========
        # print('=' * 20)
        # print(graph.context)
        # print(graph.target_func)
        # =======To delete=========
        # print(len(graph.node_labels))
        if len(graph.node_labels) > args.max_seq_length:
            # print('--')
            continue
        graphs.append(graph)

        graph.dump_into_file(args.out_path, merge=True)
        # =======Remember to recover=========
    return graphs


if __name__ == '__main__':

    path = '/home/gezhang/data/jupyter/target'
    all_graphs = []
    error_files = []

    for file in tqdm(os.listdir(path)):

        try:
            graphs = process_file(os.path.join(path, file))
            all_graphs += graphs

        except Exception as e:
            # print(e)
            error_files.append(file)
    print('[Info] get {} graphs'.format(len(all_graphs)))
    with open('error.out', 'w') as f:
        f.write('\n'.join(error_files))
    # pdb.set_trace()
