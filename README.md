# An improved label propagation algorithm, KMLPA
A Python implementation of Label Propagation Algorithm that modified with a series of pre-processing and post-processing operations, which can be used to find community in large social network.  
This algorithm model is built on the basis of [benedekrozemberczki/LabelPropagation](https://github.com/benedekrozemberczki/LabelPropagation). 

## Brief
This model is the implementation of our improved LPA, which is modified by several method to enhance the accuracy of community clustering. 
- At pre-processing phase: K-core decompose iteration numbers are used to partially initialize nodes with origin labels,then degree centrality and eigenvector centrality are added to generate comprehensive influence of each node with entropy weight method. Threshold 1 are set here to control initialize scale. 
- At updating phase: change update sequence with comprehensive influences. 
- At post-processing phase: a community merge method is used to merge small cluster into big community. Threshold 2 are set here to control merge proportion. 

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

## Datasets
We have collected several datasets to test our model (at `/data/*`), which is shown below. 
```
[Test dataset]
d.csv: x nodes y edges, Politician network
politician_edges.csv: 

[Standford large network datasets]
facebook.csv: x nodes y edges, 
twitter.csv: 

[Common datasets for study in Community Detection]
dolphins.gml: x nodes y edges, Dolphins network
karate.gml: x nodes y edges, karate network
football.gml: x nodes y edges, football network

[Dataset from our web spider]
jianshu_v0.csv: x nodes, y edges. User following network from jianshu.com
jianshu_v1.csv: x nodes, y edges. User following network from jianshu.com
jianshu_v2.csv: x nodes, y edges. User following network from jianshu.com
jianshu_v3.csv: x nodes, y edges. User following network from jianshu.com
```
We also add LFR benchmark network, which can be called only if the input path has a illegal extension as the parameter ending (extension in addition to `*.csv` and `*.gml`, such as: `*.calllfr`). 
```bash
project_path> python src/run_lpa.py -input 'path//lfr_network.calllfr'
```


## Usage Example
- After change default parameters in `param_parser.py`, run `run_lpa.py`. 
#### Model options
```
  --input               STR    Input graph path.                          Default is `\\data\\facebook.csv`.                                     
  --output              STR    Node-cluster assignment dictionary (JSON format) path.   Default is `\\output\\facebook.json`.
  --weighing            STR    Weighting strategy.                        Default is `unit`.
  --rounds              INT    Maximum number of iterations.                      Default is 20.
  --seed                INT    Initial seed (unused).                              Default is 10.
```
- Or run `run_lpa.py` at command prompt with parameter (optional). 
```bash
project_path> python src/run_lpa.py --input [input_path]
```
```bash
project_path> python src/run_lpa.py --weighting overlap
```
```bash
project_path> python src/run_lpa.py --seed 32
```
