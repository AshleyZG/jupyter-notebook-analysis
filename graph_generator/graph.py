import astunparse
import re
import json
import pdb

from constants import *


class Graph(object):
    """docstring for Graph"""

    def __init__(self, ast_nodes, target_lineno, target_node):
        super(Graph, self).__init__()
        self.target_lineno = target_lineno
        self.target_node = target_node
        self.node_labels = ['<HOLE>']
        self.custom_labels = []
        self.edges = {}
        self.target_root = None
        self.original_expression = None
        self.target_set = None
        self.target_tokens = None
        self.build_graph(ast_nodes)
        self.add_next_token()
        self.add_last_token_used()
        self.replace_target()
        self.split_original_expression()

    def build_graph(self, ast_nodes):
        '只构建 child 边'
        self.edges['Child'] = []
        next_start_index = len(self.node_labels)
        for ast_node in ast_nodes:
            next_start_index = self._build_subtree(ast_node, next_start_index)

    def _build_subtree(self, ast_node, start_index):
        assert start_index == len(
            self.node_labels), '[Error] start_index!=len(self.node_labels)'
        if type(ast_node).__module__ == '_ast':
            self.node_labels.append(type(ast_node).__name__)

            if getattr(ast_node, 'lineno', -1) == self.target_lineno and self.target_root is None:
                self.target_root = start_index
                self.original_expression = astunparse.unparse(
                    ast_node).strip().replace(' ', '')

            for key in ast_node.__dict__:
                if key in ['col_offset', 'lineno']:
                    continue
                values = getattr(ast_node, key)
                if not isinstance(values, list):
                    values = [values]
                for son_node in values:
                    self.edges['Child'].append(
                        [start_index, len(self.node_labels)])
                    next_start_index = self._build_subtree(
                        son_node, len(self.node_labels))
                    assert next_start_index == len(
                        self.node_labels), '[Error] next_start_index!=len(self.node_labels)'

        else:
            self.node_labels.append(str(ast_node))
            self.custom_labels.append(start_index)

        return len(self.node_labels)

    def add_next_token(self):
        '添加 nextToken 边'
        self.edges['NextToken'] = []
        for i in range(len(self.custom_labels) - 1):
            self.edges['NextToken'].append(
                [self.custom_labels[i], self.custom_labels[i + 1]])

    def add_last_token_used(self):
        '添加 LastLexicalUsed 边'
        self.edges['LastLexicalUsed'] = []

        label2idx = {}
        for idx in self.custom_labels:
            if self.node_labels[idx] not in label2idx:
                label2idx[self.node_labels[idx]] = idx
            else:
                self.edges['LastLexicalUsed'].append(
                    [idx, label2idx[self.node_labels[idx]]])
                label2idx[self.node_labels[idx]] = idx

    def dump_into_file(self, out_path):
        '''
        Dump the graph of a program into a file
        -------------------------------
        param:
        out_path: where to dump the graph
        '''
        graph = {"ContextGraph": {"Edges": self.edges, "NodeLabels": self.node_labels},
                 "SymbolLabels": ['<HOLE>'] + self.target_tokens + ['<eos>'],
                 "OriginalExpression": self.original_expression,
                 "HoleNode": HOLE}
        with open(out_path, 'w') as fout:
            fout.write(json.dumps(graph, ensure_ascii=False, indent=2))

    def replace_target(self):
        target_set = [self.target_root]

        for edge in self.edges['Child']:
            if edge[0] in target_set:
                if edge[1] not in target_set:
                    target_set.append(edge[1])

        new_child = []
        new_next_token = []
        new_last_lexical_used = []

        for edge in self.edges['Child']:
            if edge[0] in target_set:
                continue
            elif edge[1] in target_set:
                new_child.append([edge[0], HOLE])
            else:
                new_child.append(edge)

        for edge in self.edges['NextToken']:
            if edge[0] in target_set:
                if edge[1] not in target_set:
                    new_next_token.append([HOLE, edge[1]])
            elif edge[1] in target_set:
                new_next_token.append([edge[0], HOLE])
            else:
                new_next_token.append(edge)

        for edge in self.edges['LastLexicalUsed']:
            if edge[0] not in target_set and edge[1] not in target_set:
                new_last_lexical_used.append(edge)

        self.edges['Child'] = new_child
        self.edges['NextToken'] = new_next_token
        self.edges['LastLexicalUsed'] = new_last_lexical_used
        self.target_set = target_set

    def split_original_expression(self):
        # pdb.set_trace()
        token_lst = []
        i = 0
        index = 0
        target_tokens = [
            self.node_labels[token] for token in self.custom_labels if token in self.target_set]
        self.target_tokens = target_tokens
        return
        # for i in range(len(self.original_expression)):
        while i < len(self.original_expression):

            if index < len(target_tokens) and self.original_expression[i:].startswith(target_tokens[index]):
                token_lst.append(target_tokens[index])
                index += 1
            else:
                token_lst.append(self.original_expression[i])
            i += len(token_lst[-1])
        self.target_tokens = token_lst
