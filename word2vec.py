'compute word2vec model based on certain corpus'
import gensim
import os
from gensim.models import word2vec
import pdb
import time
import json
import itertools
import re

func_token_path = '/home/gezhang/jupyter-notebook-analysis/func_tokens.txt'
corpus = word2vec.Text8Corpus(func_token_path)
start_time = time.time()
model = word2vec.Word2Vec(corpus, window=10, size=512, min_count=4,)
print('[Info] train model: {} s'.format(time.time() - start_time))
model.save("word2vec.model")
# pdb.set_trace()
