from config import nb_path
import os
import json
import random
import re


from sklearn import feature_extraction
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans


def extract_code(ipynb_file):
    with open(ipynb_file, 'r') as f:
        notebook = json.load(f)
    print(notebook.keys())
    cell_sources = []
    if 'cells' not in notebook:
        return cell_sources
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            # codes = [clean_code(line) for line in cell['source']]
            # cell_sources += codes
            cell_sources += cell['source']
    return cell_sources


def print_cell_code(cell):
    if cell['cell_type'] == 'code':
        print(cell['source'])


def clean_code(line):
    'convert a line of code to a list of tokens'

    tokens = re.compile(r'[.():\[\]{}+-/*=><\\]+')
    inside_quote = re.compile(r'\'.*?\'')
    inside_double_quote = re.compile(r'\".*?\"')
    # result = ''
    # for line in line:
    line = re.sub(tokens, ' ', line)
    line = re.sub(inside_quote, '', line)
    line = re.sub(inside_double_quote, '', line)

    return line
    # result += line

    return result
    return re.sub(tokens, ' ', source_codes)


if __name__ == '__main__':
    files = [f for f in os.listdir(nb_path) if f.endswith('.ipynb')]
    file = random.choice(files)
    sources = extract_code(os.path.join(nb_path, file))
    cleaned_sources = [clean_code(l) for l in sources]
    print(sources)

    vectorizer = CountVectorizer()

    transformer = TfidfTransformer()

    tfidf = transformer.fit_transform(
        vectorizer.fit_transform(cleaned_sources))

    weight = tfidf.toarray()
    clf = KMeans(n_clusters=20)
    s = clf.fit(weight)
    # print(s)

    # 20个中心点
    # print(clf.cluster_centers_)

    # 每个样本所属的簇
    # print(clf.labels_)
    ans = {}
    for code, label in zip(sources, clf.labels_):
        if label not in ans:
            ans[label] = []
        else:
            ans[label].append(code)
    # print(json.dumps(ans, indent=2))
    # print(ans.values())
    for value in ans.values():
        print('='*20)
        print(''.join(value))
