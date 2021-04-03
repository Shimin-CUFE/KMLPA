# Modified Label Propagation Algorithm, KMLPA
A Python implementation of LPA, which is modified with a series of pre-process and post-process.  
This model is built on the basis of **venedekrozemberczki/LabelPropagation**. 

## Brief


## Requirements
The codebase is implemented in `Python 3.9.1`. Package versions used for development are just below.
```
networkx    2.5  
scipy   1.6.0  
pandas  1.2.0  
texttable   1.6.3  
tqdm    4.56.0  
matplotlib  3.3.3  
numpy   1.19.5  
python_louvain  0.15 ([^NOTE]: import as community)
scrapy  1.7.2  
lxml    4.4.0  
Twisted 19.2.1  
igraph  0.1.11  
snap    0.5  
```

## Datasets (/data/*)
We have collected several datasets to test our model, which is shown below. 
```
[Test dataset]
d.csv: x nodes y edges, Politician network

[Standford large network datasets]
facebook.csv: x nodes y edges, 
twitter.csv: 

[Common datasets for study in Community Detection]
dolphins.gml: x nodes y edges, Dolphins network
karate.gml: x nodes y edges, karate network
football.gml: x nodes y edges, football network

[Dataset from our web spider]
jianshu.csv: x nodes, y edges. User following network from jianshu.com
```
We also add LFR benchmark network, which can be called only if the input path has a illegal extension as the parameter ending (extension in addition to `*.csv` and `*.gml`, such as: `*.calllfr`). 
```sh
$ python src/run_lpa.py -input 'path//lfr_network.calllfr'
```


## Usage Example
- After change default parameters in `param_parser.py`, run `run_lpa.py`. 
#### Model options
```
  --input               STR    Input graph path.                          Default is `\\data\\facebook.csv`.                                     
  --assignment-output   STR    Node-cluster assignment dictionary path.   Default is `\\output\\facebook.json`.
  --weighing            STR    Weighting strategy.                        Default is `overlap`.
  --rounds              INT    Number of iterations.                      Default is 30.
  --seed                INT    Initial seed           .                   Default is 42.
```
- Or run `run_lpa.py` at command prompt with parameter (optional). 
```cmd
project_path> python src/run_lpa.py --input [input_path]
```
```cmd
project_path> python src/run_lpa.py --weighting overlap
```
```cmd
project_path> python src/run_lpa.py --seed 32
```
