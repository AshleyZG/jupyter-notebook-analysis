# jupyter-notebook-analysis
analysis for jupyter notebooks  

## Data
`/home/gezhang/data/jupyter/target` python files which import 'statsmodels', 'gensim', 'keras', 'sklearn', 'xgboost'  
`/home/gezhang/jupyter-notebook-analysis/func_tokens.txt` all functions from target pys. split by '.' '\_'. used for word2vec.  
`/home/gezhang/jupyter-notebook-analysis/graphs.txt` window_size=1 graphs  
`/home/gezhang/jupyter-notebook-analysis/single_token_graphs.txt` window_size=1, single token graphs 
`/home/gezhang/jupyter-notebook-analysis/decision_points.txt` all functions & labels, used for train  
`/home/gezhang/jupyter-notebook-analysis/graphs_last_token.txt` graphs window_size=1 , use last token as target  
`/home/gezhang/jupyter-notebook-analysis/toy_funcs_graph.txt` graphs functions list (toy )  
`/home/gezhang/jupyter-notebook-analysis/funcs_graph.txt` graphs functions list   
## Vocab
`/home/gezhang/graph-based-code-modelling/Models/vocab_window_1.json` window size=1 all graphs (cg 60000, tg 10000)  
`/home/gezhang/graph-based-code-modelling/Models/vocab_window_1_large.json` window size=1 all graphs (cg 65274, tg 19079)
`/home/gezhang/graph-based-code-modelling/Models/vocab_window_1_llarge.json` window size=1 all graphs (cg 92139, tg 30812)
`/home/gezhang/graph-based-code-modelling/Models/vocab_single_token.json` window size=1 single token graphs (cg 89779, tg 1168)
`/home/gezhang/graph-based-code-modelling/Models/vocab_last_token.json`window size=1 single token graphs ( ) last token as target
`/home/gezhang/graph-based-code-modelling/Models/vocab_only_func.json` only functions graphs vocab ()
## Model
`/home/gezhang/jupyter-notebook-analysis/classifier.pth` function classifer (decision points/nobs)   
`/home/gezhang/jupyter-notebook-analysis/word2vec.model` word2vec on function name tokens  
`/home/gezhang/graph-based-code-modelling/Models/model_window_1.pth` window_size=1, vocab(60000, 10000)   
`/home/gezhang/graph-based-code-modelling/Models/model_window_1_large.pth`window_size=1, vocab(65274,19079)  
`/home/gezhang/graph-based-code-modelling/Models/model_window_1_single_token_toy.pth`window_size=1, (cg 89779, tg 1168) 10000 graphs  
`/home/gezhang/graph-based-code-modelling/Models/model_window_1_single_token.pth`window_size=1, (cg 89779, tg 1168) 10000 graphs  
`/home/gezhang/graph-based-code-modelling/Models/model_single_last_token.pth` target = last token, single token model ()
## Log
`/home/gezhang/jupyter-notebook-analysis/nobs_similars.txt` 13832 functions occur more than 10 (all 110000 funcs)
`/home/gezhang/graph-based-code-modelling/Models/last_token_test_alternatives.txt` last token single token test alternatives