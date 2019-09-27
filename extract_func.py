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

        if func != None and self.nest == 1:
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
    global module_map
    # with open(file, 'r') as f:
    #     sources = f.read()
    funcs = []
    linenos = []
    tree = ast.parse(sources)
    visitor.visit(tree)

    if visitor.funcs != []:

        funcs = visitor.funcs
        linenos = visitor.linenos

    visitor.reset_funcs()
    module_map = {}
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


def process_file(file):
    with open(file, 'r') as f:
        sources = f.read()
    extract_module(sources=sources)

    funcs, linenos = extract_funcs_from_py(sources=sources)
    return funcs, linenos


if __name__ == '__main__':
    path = '/home/gezhang/data/jupyter/target'
    files = [f for f in os.listdir(path) if f.endswith('.py')]
    frequency_map = {}
    all_funcs = []
    err_files = []
    file2func = {}

    for f in tqdm(files):
        try:
            funcs, linenos = process_file(os.path.join(path, f))
            print(funcs)
        except Exception as e:
            print(e)
