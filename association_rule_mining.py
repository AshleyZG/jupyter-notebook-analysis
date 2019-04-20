import os
import numpy

PATH = './python2.txt'

dictionary = {}

with open(PATH, 'r') as f:
    for l in f:
        funcs = l.strip().split()
        for func in funcs:
            if func in dictionary:
                dictionary[func] += 1
            else:
                dictionary[func] = 1


idx2word = list(dictionary.keys())

numpy.save('dict.npy', idx2word)


word2idx = {}
for i, word in enumerate(idx2word):
    word2idx[word] = i

# word2idx


with open(PATH, 'r') as f,\
        open('asr_large.txt', 'w') as fout:
    for l in f:
        funcs = l.strip().split()
        seq = ' '.join([str(word2idx[func]) for func in funcs if not func.startswith(
            'matplotlib') and not func.startswith('get_ipython') and not func.startswith('tensorflow') and func != 'len' and func != 'print'])
        fout.write(seq)
        fout.write('\n')
