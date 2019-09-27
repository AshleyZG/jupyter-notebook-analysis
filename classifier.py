# encoding=utf-8
# Created by Ge Zhang @ 2019
# Contact zhangge9194@pku.edu.cn
#
# Linear classifier of decision points
# decision points: any function starts with key_lib (config.py)
'classifier of decision points'

import numpy as np
import os
from tqdm import tqdm
import pdb
import random
import json
import torch
import torch.nn as nn
import torch.optim as optim

from torch.utils import data


from word2vec import load_model
from extract_func import process_file
from config import key_libs, SEED


random.seed(SEED)
os.environ["CUDA_VISIBLE_DEVICES"] = "1"
log_size = 10
clip = 1
n_epoch = 50
n_tolerance = 2
idx2word, vectors, wv_model = load_model()
word2idx = {word: i for i, word in enumerate(idx2word)}


def create_dataset():
    path = '/home/gezhang/data/jupyter/target'
    files = [f for f in os.listdir(path) if f.endswith('.py')]

    all_funcs = []
    for file in tqdm(files):
        try:
            funcs, _ = process_file(os.path.join(path, file))
            all_funcs.append(funcs)
        except:
            pass

    with open('./decision_points.txt', 'a') as f:
        for funcs in all_funcs:
            for func in funcs:
                if any([func.startswith(lib) for lib in key_libs]):
                    label = 1
                else:
                    label = 0
                f.write('{}\t{}\n'.format(func, label))


class FunctionDataset(data.Dataset):
    """docstring for FunctionDataset"""

    def __init__(self, type='train'):
        super(FunctionDataset, self).__init__()

        dataset = {}
        with open('./decision_points.txt', 'r') as f:
            for l in tqdm(f):
                item = l.strip().split('\t')

                if any([t not in idx2word for t in item[0].replace('.', ' ').split()]):
                    continue
                dataset[item[0]] = item[1]

        target = [f for f in dataset if dataset[f] == '1']
        noise = [f for f in dataset if dataset[f] == '0']

        random.shuffle(target)
        random.shuffle(noise)
        if type == 'train':
            target = target[:int(0.8 * len(target))]
        elif type == 'dev':
            target = target[int(0.8 * len(target)):int(0.9 * len(target))]
        elif type == 'test':
            target = target[int(0.9 * len(target)):]
        else:
            raise NotImplementedError
        noise = noise[:int(5 * len(target))]

        data = target + noise
        random.shuffle(data)

        self.dataset = dataset
        self.data = data

    def __getitem__(self, index):
        func = self.data[index]
        label = int(self.dataset[func])
        tokens = func.replace('.', ' ').split()
        ids = [word2idx[t] for t in tokens]
        embs = np.array([vectors[i] for i in ids])
        mean_emb = np.mean(embs, axis=0)

        return mean_emb, label

    def __len__(self):
        return len(self.data)


def my_collate_fn(batch):
    targets = torch.tensor([item[1] for item in batch])
    embs = np.array([item[0] for item in batch])
    embs = torch.tensor(embs)

    return embs, targets


class Classifier(nn.Module):
    """docstring for Classifier"""

    def __init__(self):
        super(Classifier, self).__init__()
        # self.arg = arg
        self.linear = nn.Linear(vectors.shape[1], 2)

    def forward(self, embs):
        probs = self.linear(embs)

        return probs


def train():
    global n_tolerance
    train_dataset = FunctionDataset()
    train_data_loader = data.DataLoader(
        train_dataset, batch_size=512, collate_fn=my_collate_fn)
    dev_dataset = FunctionDataset(type='dev')
    dev_data_loader = data.DataLoader(
        dev_dataset, batch_size=512, collate_fn=my_collate_fn)

    model = Classifier()
    model.cuda()
    total_loss = 0
    best_loss = None

    criterion = criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters())

    for epoch in range(n_epoch):
        model.train()
        for i, (embs, targets) in enumerate(train_data_loader):
            optimizer.zero_grad()
            embs = embs.cuda()
            targets = targets.cuda()

            output = model(embs)

            loss = criterion(output, targets)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), clip)
            optimizer.step()
            total_loss += loss.data

            if i != 0 and i % log_size == 0:
                print('| epoch {} | {}/{} | loss {} |'.format(epoch,
                                                              i, len(train_data_loader), total_loss / log_size))
                total_loss = 0
        total_loss = 0
        model.eval()
        with torch.no_grad():
            for embs, targets in dev_data_loader:
                embs = embs.cuda()
                targets = targets.cuda()

                output = model(embs)

                loss = criterion(output, targets)
                total_loss += loss.data
        eval_loss = total_loss / len(dev_data_loader)
        print('| epoch {} | loss {} |'.format(
            epoch, eval_loss))
        if best_loss is None or best_loss > eval_loss:
            best_loss = eval_loss
            torch.save(model.state_dict(), './classifier.pth')
        else:
            n_tolerance -= 1
        if n_tolerance == 0:
            break


def eval():
    model_path = './classifier.pth'
    test_dataset = FunctionDataset()
    test_data_loader = data.DataLoader(
        test_dataset, batch_size=512, collate_fn=my_collate_fn)

    model = Classifier()
    model.load_state_dict(torch.load(model_path))
    model.cuda()
    model.eval()
    n_example = 0
    n_correct = 0
    with torch.no_grad():

        for i, (embs, targets) in enumerate(test_data_loader):

            embs = embs.cuda()
            # targets = targets.cuda()

            output = model(embs)
            prob = torch.nn.functional.softmax(output, dim=1)
            pred = torch.squeeze(torch.topk(prob, 1)[1]).tolist()
            targets = targets.tolist()

            for t, p in zip(targets, pred):
                n_example += 1
                if t == p:
                    n_correct += 1
            if i != 0 and i % 100 == 0:
                print('| Porgress | {}/{} |'.format(i, len(test_data_loader)))
            # pdb.set_trace()
    print('| Model {} | Accuracy {} |'.format(
        model_path, n_correct / n_example))
    # raise NotImplementedError


def predict(model, tokens):
    try:
        embs = np.array([vectors[word2idx[t]] for t in tokens])
        mean_emb = np.mean(embs, axis=0)
        src = torch.tensor(mean_emb)
        output = model(src)
        prob = torch.nn.functional.softmax(output)
        pred = torch.topk(prob, 1)[1].item()

        return pred
    except:
        return -1


def predict_batch(model, batch_tokens):
    batch_tokens = [tokens for tokens in batch_tokens if all(
        [t in word2idx for t in tokens])]
    embs = [np.array([vectors[word2idx[t]] for t in tokens])
            for tokens in batch_tokens]
    mean_embs = np.array([np.mean(emb, axis=0) for emb in embs])
    topk = [wv_model.similar_by_vector(
        tokens[-1], topn=10) for tokens in batch_tokens]

    src = torch.tensor(mean_embs)
    output = model(src)
    prob = torch.nn.functional.softmax(output, dim=1)
    pred = torch.squeeze(torch.topk(prob, 1, dim=1)[1]).tolist()
    return pred, topk


def test(file):
    funcs, linenos = process_file(file)
    model = Classifier()
    # pdb.set_trace()
    model.load_state_dict(torch.load('./classifier.pth'))
    for func, lineno in zip(funcs, linenos):
        tokens = func.replace('.', ' ').replace('_', ' ').split()
        pred = predict(model, tokens)
        if pred == 1:
            print(func, pred, lineno)


def add_annotation(file):
    with open(file, 'r') as f:
        lines = f.read().split('\n')

    funcs, linenos = process_file(file)
    model = Classifier()
    model.load_state_dict(torch.load('./classifier.pth'))
    for func, lineno in zip(funcs, linenos):
        tokens = func.replace('.', ' ').replace('_', ' ').split()
        pred = predict(model, tokens)
        if pred == 1:
            print(func, pred, lineno)
            lines[lineno - 1] += '  # DECISIONPOINT'

    with open('./temp.out', 'w') as fout:
        fout.write('\n'.join(lines))


def find_alternative():
    data = []
    with open('nobs_similars_100.txt', 'r') as f:
        for l in f:
            data.append(json.loads(l))

    for sample in tqdm(data):

        sample['alternatives'] = wv_model.most_similar(
            sample['function'], topn=20)

    with open('a.out', 'w') as f:
        for d in data:
            f.write(json.dumps(d, ensure_ascii=False))
            f.write('\n')


if __name__ == '__main__':
    find_alternative()
    assert False
    model = Classifier()
    model.load_state_dict(torch.load('./classifier.pth'))

    with open('./top_100.txt', 'r') as f:
        freq_map = json.load(f)

    print('{} functions'.format(len(freq_map)))

    funcs = list(freq_map.keys())
    funcs = [f for f in funcs if all([t in word2idx for t in f.split('.')])]
    batch_size = 64
    preds = []
    similars = []
    for i in range(0, len(funcs), batch_size):
        pred, topk = predict_batch(model, [f.split('.')
                                           for f in funcs[i:i + batch_size]])
        preds += pred
        similars += topk
        print('{}/{}'.format(i, len(funcs)))
    assert len(funcs) == len(preds), '{} funcs but {} preds'.format(
        len(funcs), len(preds))
    assert len(similars) == len(funcs), '{} funcs but {} similars'.format(
        len(funcs), len(similars))

    for f, p, s in zip(funcs, preds, similars):

        result = {"function": f,
                  "is_decision_point": p,
                  "n_occur": freq_map[f],
                  "most_similar": [item for item in s if item[1] >= 0.5]}

        with open('nobs_similars_100.txt', 'a') as fout:
            fout.write(json.dumps(result, ensure_ascii=False))
            fout.write('\n')

    print('[Info] writing {} functions into {}'.format(
        len(funcs), 'nobs_similars_100.txt'))
