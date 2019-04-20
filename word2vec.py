import gensim
import os
from gensim.models import word2vec

sentences = word2vec.Text8Corpus(
    '/home/zhangge/jupyter-notebook-analysis/python2.txt')
model = word2vec.Word2Vec(sentences, window=16, size=200, min_count=4,)

# print(model.similarity('dfx.to_csv', 'df.to_csv'))
# print(model.similarity('乔峰', '慕容复'))
print(model.most_similar("sklearn.metrics.r2_score"))
print(model.most_similar("sklearn.lda.LDA"))
print(model.most_similar("sklearn.naive_bayes.MultinomialNB.fit"))
# print(model.most_similar("sklearn.decoposition.PCA"))
print(model.most_similar("sklearn.metrics.accuracy_score"))
# print(model.most_similar("scipy.signal.medfilt", topn=20))
# print(model.most_similar(u"softmax"))
# print(model.most_similar(u"xgb_model.predict"))
# model.most_similar(positive=['woman', 'king'], negative=['man'], topn=1)
