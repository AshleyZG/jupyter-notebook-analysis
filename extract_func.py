'extract function calls and replace abbreviations by full names'
import ast
import os
import random
from config import *
from preprocess import *

module_map = {}


class Visitor(ast.NodeVisitor):
    def __init__(self):
        self.nest = 0
        self.funcs = []

    def generic_visit(self, node):

        ast.NodeVisitor.generic_visit(self, node)

    def visit_Call(self, node):
        self.nest += 1
        func = self.process_func(node.func)
        if func != None and self.nest == 1:
            self.funcs.append(func)
            # print(func, node.lineno)
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


def extract_funcs_from_py(file):
    with open(file, 'r') as f:
        sources = f.read()
    funcs = []
    tree = ast.parse(sources)
    visitor.visit(tree)

    if visitor.funcs != []:

        funcs = visitor.funcs
        visitor.reset_funcs()

    return funcs


def extract_module(file):
    with open(file, 'r') as f:
        sources = f.read()
    tree = ast.parse(sources)
    mdvisitor.visit(tree)


errors = []


def process_file(file):
    try:
        extract_module(file)
        funcs = extract_funcs_from_py(file)
        with open('temp12.txt', 'a') as fout:
            fout.write(' '.join(funcs))
            fout.write('\n')
    except Exception as e:

        errors.append(file)


files = [f for f in os.listdir(nb_path) if f.endswith('.py')]


for file in tqdm(files[110000:]):
    process_file(os.path.join(nb_path, file))
