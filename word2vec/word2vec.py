# encoding=utf-8
# created by Ge Zhang @ 2019
# contact zhangge9194@pku.edu.cn
#
# this is a start point of the jupyter notebook project
# train word2vec model based on function lists
# find alternatives by cos similarity of function vectors

import gensim
import os
from gensim.models import word2vec
import pdb
import time
import json
import itertools
import re
import numpy as np


def train():
    func_token_path = '/home/gezhang/jupyter-notebook-analysis/word2vec_train.txt'
    corpus = word2vec.Text8Corpus(func_token_path)
    start_time = time.time()
    model = word2vec.Word2Vec(corpus, window=10, size=512, min_count=0,)
    print('[Info] train model: {} s'.format(time.time() - start_time))
    model.save("wv_total.model")


def load_model():
    model_path = 'wv_total.model'
    wv_path = 'wv_total.model.wv.vectors.npy'

    model = word2vec.Word2Vec.load(model_path)
    idx2word = model.wv.index2word
    vectors = np.load(wv_path)
    return idx2word, vectors, model


if __name__ == '__main__':
    # train()
    # model_path = 'word2vec.model'
    model = word2vec.Word2Vec.load('wv_total.model')
