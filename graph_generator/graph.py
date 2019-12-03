import astunparse
import re
import json
import random
import pdb
from .parse_python import parse_snippet
from constants import HOLE
# from extract_func import extract_funcs_from_code


# TARGET_TOKENS = []
# with open('./decision_points.txt', 'r') as f:
#     for l in f:
#         if l.strip()[-1] == '0':
#             continue
#         func = l.split('\t')[0]
#         tokens = func.split('.')[1:]
#         TARGET_TOKENS += tokens
# TARGET_TOKENS = list(set(TARGET_TOKENS))


class Graph(object):
    """docstring for Graph"""

    def __init__(self, ast_nodes, target_lineno, target_node, file, single_token, only_func, target_func=None):
        super(Graph, self).__init__()
        self.target_lineno = target_lineno
        self.target_node = target_node
        self.single_token = single_token
        self.only_func = only_func
        self.target_func = target_func
        self.file = file
        self.node_labels = ['<HOLE>']
        self.custom_labels = []
        self.edges = {}
        self.target_root = None
        self.original_expression = None
        self.target_set = None
        self.target_tokens = None
        self.context = ''.join([astunparse.unparse(node)
                                for node in ast_nodes])
        return

        self.build_graph(ast_nodes)
        self.add_next_token()
        self.add_last_token_used()
        # return
        if single_token:
            self.new_replace_target()
        elif only_func:
            self.replace_target_only_func()
        else:
            self.replace_target()
        # pdb.set_trace()
        self.split_original_expression(single_token, only_func)
        # pdb.set_trace()

    def parse_snippet(self, snippet):
        nodes = parse_snippet(snippet)
        return nodes
        raise NotImplementedError

    def build_graph(self, ast_nodes):
        '只构建 child 边'
        self.edges['Child'] = []
        next_start_index = len(self.node_labels)
        for ast_node in ast_nodes:
            next_start_index = self._build_subtree(ast_node, next_start_index)

    def _build_subtree(self, ast_node, start_index):
        '把每一个 ast node 变成只有 child 边的 tree'
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

    def dump_into_file(self, out_path, merge=False):
        '''
        Dump the graph of a program into a file
        -------------------------------
        param:
        out_path: where to dump the graph
        '''
        # if self.single_token:
        #     symbol_labels = self.target_tokens
        # elif self.only_func:
        #     # print(self.target_tokens)
        #     # symbol_labels = [self.node_labels[l] for l in self.target_tokens]
        #     symbol_labels = self.target_tokens
        #     # raise NotImplementedError
        # else:
        #     symbol_labels = ['<HOLE>'] + self.target_tokens + ['<eos>']
        symbol_labels = self.target_func.split('.')
        graph = {"ContextGraph": {"Edges": self.edges, "NodeLabels": self.node_labels},
                 "SymbolLabels": symbol_labels,
                 "OriginalExpression": self.original_expression,
                 "HoleNode": HOLE,
                 "File": self.file,
                 "Context": self.context,
                 # "ContextID": [l for l in self.custom_labels if l not in symbol_labels],
                 "TargetTokens": self.target_tokens,
                 "TargetLineno": self.target_lineno,
                 "TargetFunc": self.target_func}
        # pdb.set_trace()
        if merge:
            with open(out_path, 'a') as fout:
                fout.write(json.dumps(graph, ensure_ascii=False))
                fout.write('\n')

        else:
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

    def new_replace_target(self):
        target_set = [self.target_root]

        for edge in self.edges['Child']:
            if edge[0] in target_set:
                if edge[1] not in target_set:
                    target_set.append(edge[1])
        custom_labels = [i for i in target_set if i in self.custom_labels]
        # 选择具体的预测 token
        # pdb.set_trace()
        # =========Original Version =======
        # target = [l for l in custom_labels if self.node_labels[l]
        #           in TARGET_TOKENS][-1]
        # ========= Temp Edit============
        last_token = self.target_func.split('.')[-1]
        for l in custom_labels:
            if self.node_labels[l] == last_token:
                target = l
        # ==========Remember to delete======

        self.target_tokens = target
        self.original_expression = self.node_labels[target]
        new_child = []
        new_next_token = []
        new_last_lexical_used = []

        for edge in self.edges['Child']:
            if edge[0] == target:

                new_child.append([HOLE, edge[1]])
            elif edge[1] == target:
                new_child.append([edge[0], HOLE])
            else:
                new_child.append(edge)

        for edge in self.edges['NextToken']:
            if edge[0] == target:
                new_next_token.append([HOLE, edge[1]])

            elif edge[1] == target:
                new_next_token.append([edge[0], HOLE])
            else:
                new_next_token.append(edge)

        for edge in self.edges['LastLexicalUsed']:
            if edge[0] != target and edge[1] != target:
                new_last_lexical_used.append(edge)

        self.edges['Child'] = new_child
        self.edges['NextToken'] = new_next_token
        self.edges['LastLexicalUsed'] = new_last_lexical_used
        self.target_set = target_set

    def replace_target_only_func(self):
        target_set = [self.target_root]

        for edge in self.edges['Child']:
            if edge[0] in target_set:
                if edge[1] not in target_set:
                    target_set.append(edge[1])
        custom_labels = [i for i in target_set if i in self.custom_labels]
        # 选择具体的预测 token
        target_line = astunparse.unparse(self.target_node)

        target, _ = extract_funcs_from_code(target_line)

        target = target[0].split('.')
        self.original_expression = target
        candidate_id = [l for l in target_set if l in self.custom_labels]
        candidate_label = [self.node_labels[l] for l in candidate_id]
        candidate_map = {l: i for i, l in zip(candidate_id, candidate_label)}
        target = [candidate_map[t] for t in target]

        self.target_tokens = target

        new_child = []
        new_next_token = []
        new_last_lexical_used = []

        for edge in self.edges['Child']:
            if edge[0] in target and edge[1] in target:
                pass

            elif edge[1] in target:
                new_child.append([edge[0], HOLE])

            elif edge[0] in target:
                new_child.append([HOLE, edge[1]])
            else:
                new_child.append(edge)

        for edge in self.edges['NextToken']:
            if edge[0] in target and edge[1] in target:
                pass
            elif edge[1] in target:
                new_next_token.append([edge[0], HOLE])

            elif edge[0] in target:
                new_next_token.append([HOLE, edge[1]])
            else:
                new_next_token.append(edge)

        for edge in self.edges['LastLexicalUsed']:
            if edge[0] in target or edge[1] in target:
                pass
            else:
                new_last_lexical_used.append(edge)

        # self.edges['Child'] = new_child
        # self.edges['NextToken'] = new_next_token
        # self.edges['LastLexicalUsed'] = new_last_lexical_used
        self.target_set = target_set

    def split_original_expression(self, single_token, only_func):

        if single_token:
            return
        elif only_func:
            return
        else:
            token_lst = []
            i = 0
            index = 0
            target_tokens = [
                self.node_labels[token] for token in self.custom_labels if token in self.target_set]
            self.target_tokens = target_tokens
            return

        while i < len(self.original_expression):

            if index < len(target_tokens) and self.original_expression[i:].startswith(target_tokens[index]):
                token_lst.append(target_tokens[index])
                index += 1
            else:
                token_lst.append(self.original_expression[i])
            i += len(token_lst[-1])
        self.target_tokens = token_lst


# class NewGraph(Graph):
#     """docstring for NewGraph"""

#     def __init__(self, arg):
#         super(NewGraph, self).__init__()
#         self.arg = arg

class MetaGraph(object):
    """docstring for MetaGraph"""

    def __init__(self, ast_nodes, target_lineno, target_node, file, target_func, funcs=None):
        super(MetaGraph, self).__init__()
        # self.arg = arg
        self.target_lineno = target_lineno
        self.target_node = target_node
        self.target_func = target_func
        self.file = file
        self.funcs = funcs
        self.custom_labels = []
        self.edges = {}
        self.target_root = None
        self.original_expression = None
        self.target_set = None
        self.target_tokens = None
        self.context = ''.join([astunparse.unparse(node)
                                for node in ast_nodes])
        self.nodes = self.parse_snippet()

    def __len__(self):
        return len(self.nodes)

    def get_metadata(self):
        """
        return json string of a graph, containing all metadata
        """
        # pdb.set_trace()
        metadata = {"target_lineno": self.target_lineno,
                    "file": self.file,
                    "context": self.context,
                    "target_func": self.target_func,
                    "nodes": self.nodes,
                    "funcs": self.funcs}
        # raise NotImplementedError
        return metadata

    def dump_into_file(self, out_path, merge=False):
        '''
        Dump the graph of a program into a file
        -------------------------------
        param:
        out_path: where to dump the graph
        '''
        metadata = self.get_metadata()
        if merge:
            with open(out_path, 'a') as fout:
                fout.write(json.dumps(metadata, ensure_ascii=False))
                fout.write('\n')

        else:
            with open(out_path, 'w') as fout:
                fout.write(json.dumps(metadata, ensure_ascii=False, indent=2))

    def parse_snippet(self):
        nodes = json.loads(parse_snippet(self.context))

        assert isinstance(nodes, list)
        # print('-'*20)
        # print(self.context)
        # print(nodes)
        # print(len(nodes))
        return nodes
