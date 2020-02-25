# encoding=utf-8
# Created by Ge Zhang @ 2019
# Contact zhangge9194@pku.edu.cn
#
# extract all functions from py files
# api: process_file()

import ast
import os
import random
import json
from tqdm import tqdm
import pdb
import re

from config import *


module_map = {}


class Visitor(ast.NodeVisitor):
    def __init__(self):
        self.nest = 0
        self.funcs = []
        self.linenos = []

    def generic_visit(self, node):

        ast.NodeVisitor.generic_visit(self, node)

    def visit_Call(self, node):
        self.nest += 1
        func = self.process_func(node.func)

        # if func != None and self.nest == 1:
        if func != None:
            self.funcs.append(func)
            self.linenos.append(node.lineno)

        self.generic_visit(node)

        self.nest -= 1

    def process_func(self, node):
        if isinstance(node, ast.Attribute):
            prefix = self.process_func(node.value)
            if prefix is None:
                return module_map.get(node.attr, node.attr)
            else:
                return module_map.get(prefix, prefix) + '.' + node.attr
        elif isinstance(node, ast.Name):
            return module_map.get(node.id, node.id)
        elif isinstance(node, ast.Call):
            return self.process_func(node.func)
        else:
            self.generic_visit(node)

    def reset_funcs(self):
        self.funcs = []
        self.linenos = []
        self.nest = 0


class ModuleVisitor(ast.NodeVisitor):

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Assign(self, node):

        if isinstance(node.value, ast.Call):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    module_map[target.id] = visitor.process_func(
                        node.value.func)
        else:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    module_map[target.id] = None

        self.generic_visit(node)

    def visit_Import(self, node):
        for module in node.names:
            if module.asname is not None:
                module_map[module.asname] = module.name
            else:
                module_map[module.name] = module.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        top_module = node.module
        for module in node.names:
            if module.asname is None:
                module_map[module.name] = '{}.{}'.format(
                    top_module, module.name)
            else:
                module_map[module.asname] = '{}.{}'.format(
                    top_module, module.name)
        self.generic_visit(node)

    def visit_alias(self, node):
        self.generic_visit(node)


visitor = Visitor()
mdvisitor = ModuleVisitor()


def extract_funcs_from_py(file=None, sources=None):
    """
    sources is file.read()
    must pass **sources**
    """

    funcs = []
    linenos = []
    tree = ast.parse(sources)
    visitor.visit(tree)

    if visitor.funcs != []:
        funcs = visitor.funcs
        linenos = visitor.linenos

    return funcs, linenos


def extract_module(file=None, sources=None):
    """
    sources is file.read()
    must pass **sources**
    """
    # with open(file, 'r') as f:
    #     sources = f.read()
    tree = ast.parse(sources)
    mdvisitor.visit(tree)


def process_file(file, content=None):
    global module_map

    if content != None:
        sources = content
    else:
        with open(file, 'r') as f:
            sources = f.read()

    snippets = re.split(r"# In\[[\s0-9]+\]:", sources)

    funcs = []
    linenos = []
    n_pre_lines = 0
    for snippet in snippets:

        extract_module(sources=snippet)

        s_funcs, s_linenos = extract_funcs_from_py(sources=snippet)
        s_linenos = [l + n_pre_lines for l in s_linenos]
        funcs += s_funcs
        linenos += s_linenos

        visitor.reset_funcs()
        n_pre_lines += len(snippet.split('\n')) - 1

    module_map = {}

    return funcs, linenos


def temp_process_file(file, content=None):
    global module_map

    if content != None:
        sources = content
    else:
        with open(file, 'r') as f:
            sources = f.read()

    snippets = re.split(r"# In\[[\s0-9]+\]:", sources)

    funcs = []
    linenos = []
    n_pre_lines = 0
    for snippet in snippets:
        try:
            extract_module(sources=snippet)

            s_funcs, s_linenos = extract_funcs_from_py(sources=snippet)
            s_linenos = [l + n_pre_lines for l in s_linenos]
            # funcs += s_funcs
            # linenos += s_linenos
            funcs.append(s_funcs)
            linenos.append(s_linenos)

        except:
            funcs.append([])
            linenos.append([])
            # pass
        visitor.reset_funcs()
        n_pre_lines += len(snippet.split('\n')) - 1

    module_map = {}

    return funcs, linenos


if __name__ == '__main__':

    files = ['/projects/bdata/jupyter/_7_1/nb_1002722.py',
             '/projects/bdata/jupyter/_7_1/nb_1183716.py',
             '/projects/bdata/jupyter/_7_1/nb_1089165.py',
             '/projects/bdata/jupyter/_7_1/nb_1090484.py',
             '/projects/bdata/jupyter/_7_1/nb_1034447.py',
             '/projects/bdata/jupyter/_7_1/nb_1234699.py',
             '/projects/bdata/jupyter/_7_1/nb_1089313.py',
             '/projects/bdata/jupyter/_7_1/nb_1005070.py',
             '/projects/bdata/jupyter/_7_1/nb_1221634.py',
             '/projects/bdata/jupyter/_7_1/nb_1183943.py',
             '/projects/bdata/jupyter/_7_1/nb_1122022.py',
             '/projects/bdata/jupyter/_7_1/nb_1226996.py',
             '/projects/bdata/jupyter/_7_1/nb_1138666.py',
             '/projects/bdata/jupyter/_7_1/nb_1245037.py',
             '/projects/bdata/jupyter/_7_1/nb_1022912.py',
             '/projects/bdata/jupyter/_7_1/nb_1116374.py',
             '/projects/bdata/jupyter/_7_1/nb_1068488.py',
             '/projects/bdata/jupyter/_7_1/nb_1163520.py',
             '/projects/bdata/jupyter/_7_1/nb_1051445.py',
             '/projects/bdata/jupyter/_7_1/nb_1026834.py',
             '/projects/bdata/jupyter/_7_1/nb_1202205.py',
             '/projects/bdata/jupyter/_7_1/nb_1005207.py',
             '/projects/bdata/jupyter/_7_1/nb_1149480.py',
             '/projects/bdata/jupyter/_7_1/nb_1058499.py',
             '/projects/bdata/jupyter/_7_1/nb_1215918.py',
             '/projects/bdata/jupyter/_7_1/nb_1236355.py',
             '/projects/bdata/jupyter/_7_1/nb_1221697.py',
             '/projects/bdata/jupyter/_7_1/nb_1240128.py',
             '/projects/bdata/jupyter/_7_1/nb_1223629.py',
             '/projects/bdata/jupyter/_7_1/nb_1024739.py',
             '/projects/bdata/jupyter/_7_1/nb_1031433.py',
             '/projects/bdata/jupyter/_7_1/nb_1109134.py',
             '/projects/bdata/jupyter/_7_1/nb_1203216.py',
             '/projects/bdata/jupyter/_7_1/nb_1242794.py',
             '/projects/bdata/jupyter/_7_1/nb_1227519.py',
             '/projects/bdata/jupyter/_7_1/nb_1161031.py',
             '/projects/bdata/jupyter/_7_1/nb_1183781.py',
             '/projects/bdata/jupyter/_7_1/nb_1222945.py',
             '/projects/bdata/jupyter/_7_1/nb_1234234.py',
             '/projects/bdata/jupyter/_7_1/nb_1159388.py',
             '/projects/bdata/jupyter/_7_1/nb_1090152.py',
             '/projects/bdata/jupyter/_7_1/nb_1138647.py',
             '/projects/bdata/jupyter/_7_1/nb_1043186.py',
             '/projects/bdata/jupyter/_7_1/nb_1189833.py',
             '/projects/bdata/jupyter/_7_1/nb_1068026.py',
             '/projects/bdata/jupyter/_7_1/nb_1105414.py']

    file2funcs = {}
    file2linenos = {}
    for f in tqdm(files):

        funcs, linenos = temp_process_file(f)
        file2funcs[f] = funcs
        file2linenos[f] = linenos
    with open('./python2_file2funcs.json', 'w') as fout:
        json.dump({"file2funcs": file2funcs,
                   "file2linenos": file2linenos
                   }, fout)
    pdb.set_trace()

    # print(nb_path)
    # notebooks = [f for f in os.listdir(nb_path) if f.endswith('.py')]
    # results = {}
    # with open('file_funcs.json', 'r') as f:
    #     results = json.load(f)
    # print(len(results))
    # pdb.set_trace()
    # for nb in tqdm(notebooks):
    #     if nb in results:
    #         continue
    #     try:
    #         funcs, linenos = process_file(os.path.join(nb_path, nb))
    #         results[nb] = {"funcs": funcs,
    #                        "linenos": linenos}
    #     except:
    #         pass
    # with open('file_funcs.json', 'w') as fout:
    #     json.dump(results, fout, ensure_ascii=False, indent=2)
