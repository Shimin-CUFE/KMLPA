import random
import time
from random import randint
import joblib
from joblib import Parallel, delayed
import time
import numpy as np
import os
import networkx as nx
import subprocess as sb
import MiseEnFormeSortieFScore as mise
import logging
import signal


# Importation of the graph, the dictionnary of the communities for each node and the ground-truth communities.
# The function takes a graph, the name of the ground-truth file (it has to be a text file with a line for each community
# with the node names) and the path to your global community detection repository.
def importGraphElements(graph, GTFile, path):
    import igraph as ig
    g = ig.Graph.Read_Ncol(path + graph)

    # creation of a tuple list (id_node,id of the communities he belongs to)
    groundT = path + GTFile
    nbComParNoeud = {}
    nodes = set()
    for idx, line in enumerate(open(groundT, "r")):
        line = line.rstrip()
        fields = line.split("\t")
        for col in fields:
            if col in nodes:
                nbComParNoeud[col].append(idx)
            else:
                nbComParNoeud[col] = [idx]
                nodes.add(col)

    # Creation of a dictionnary {name :index} for the nodes.
    nomIndice = {}
    for node in g.vs:
        nomIndice[node['name']] = node.index

    return {'g': g, 'nbComParNoeud': nbComParNoeud, 'GT': groundT, 'nomIndice': nomIndice}


# Function that applies to a given subgraph the community detection algorithm of choice and returns a dictionnary
# {community id : list of nodes}.
# The parameters are the name of the algorithm (InfoIG for igraph's infomap, FastGreedy, BigClam, CPM, InfoMap for snap's infomap),
# The subgraph of the original graph we get from the Performance function below, the name of the  dictionnary to store the
# results, the ath to the global repository and the path to the snap library.
def ChoixAlgo(algo, subgraph, commClus, path, SnapPath):
    if algo == "InfoIG":
        clus = subgraph.community_infomap()
        comm = list(clus)
    elif algo == "FastGreedy":
        subgraph = subgraph.as_undirected()
        clus = subgraph.community_fastgreedy()
        clus = clus.as_clustering()
        comm = list(clus)
    elif algo == "BigClam" or algo == "CPM" or algo == "InfoMap":
        text_file = open(SnapPath + "examples/Output.txt", "w")

    if algo in ["FastGreedy", "InfoIG"]:
        commClus = {}
        for indx, it in enumerate(comm):
            nodes = []
            for n in it:
                nodes.append(n)
            commClus[indx] = nodes
    else:
        for es in subgraph.es:
            text_file.write(str(es.tuple[0]) + "\t" + str(es.tuple[1]) + "\n")
        text_file.close()

    if algo == "BigClam":
        sb.call("./bigclam -i:../Output.txt -c:-1 -mc:2 -xc:100", cwd=SnapPath + "examples/bigclam", shell=True)
        text_file = open(SnapPath + "examples/bigclam/cmtyvv.txt", "r")
    elif algo == "CPM":
        sb.call(SnapPath + "examples/cliques/cliquesmain -i:../Output.txt -k:5", cwd=SnapPath + "examples/cliques",
                shell=True)
        text_file = open(SnapPath + "examples/cliques/cpm-Output.txt", "r")
    elif algo == "InfoMap":
        sb.call("./community -i:../Output.txt -a:3", cwd=SnapPath + "examples/community", shell=True)
        mise.MiseEnFormeSortie(SnapPath + "examples/community/communities.txt",
                               SnapPath + "examples/community/comInfo.txt")
        text_file = open(SnapPath + "examples/community/comInfo.txt", "r")

    if algo == "CPM":
        for indx, line in enumerate(text_file):
            if indx > 1:
                line = line.rstrip()
                fields = line.split("\t")
                noeuds = []
                for col in fields:
                    noeuds.append(col)
                commClus[indx] = noeuds
        text_file.close()
    elif algo in ["BigClam", "InfoMap"]:
        for indx, line in enumerate(text_file):
            line = line.rstrip()
            fields = line.split("\t")
            noeuds = []
            for col in fields:
                noeuds.append(col)
            commClus[indx] = noeuds
        text_file.close()
    print('nb de com détectées: ' + str(len(commClus)))
    return commClus


# Function to compute the F-Score
def calculFScore(i, j):
    i = [int(x) for x in i]
    j = [int(x) for x in j]
    inter = set(i).intersection(set(j))
    precision = len(inter) / float(len(j))
    recall = len(inter) / float(len(i))
    if recall == 0 and precision == 0:
        fscore = 0
    else:
        fscore = 2 * (precision * recall) / (precision + recall)
    return fscore


# We take the highest F-Score bewteen every detected community and every ground-truth community
def loop_FScore_1(i, GT):
    res = [calculFScore(i, value) for value in GT.itervalues()]
    interMax = max(res)
    return interMax


# We take the highest F-Score bewteen every ground-truth community and every detected community
def loop_FScore_2(i, GT, commClus):
    res = [calculFScore(i, value) for value in commClus.itervalues()]
    interMax = max(res)
    return interMax


# Handler for the time out
def handler(signum, frame):
    print("The algorithm is taking too much time")
    raise Exception("The Algorithm was taking too long on this subgraph - Repetition of the iteration")


# Evaluation of the performance (F-Score or accuracy in the number of communities) for an algorithm (algo) on a given number of
# subgraphs (nbSG) with a limited size (tailleMaxsg) and computation time in seconds (MaxTimeSec) by subgraph.
# We need a path to the global repository (path) and to the snap library. THe function returns the globlal F-Score or accuracy
# in the number of communities (mean on all the subgraphs).


def Performance(GraphElements, algo, nbSG, tailleMaxsg, path, SnapPath, mesure, MaxTimeSec):
    logging.basicConfig(filename=path + 'performance.log', filemode='w', level=logging.DEBUG)
    start = time.time()
    g = GraphElements['g']
    nbComParNoeud = GraphElements['nbComParNoeud']
    nomIndice = GraphElements['nomIndice']
    FileGT = GraphElements['GT']

    Score = 0
    random.seed(11)

    for i in range(0, nbSG):
        commClus = {}
        successful = False
        print("sous-graphe num " + str(i))
        while len(commClus) == 0 or successful == False:
            tailleSG = tailleMaxsg + 1
            while tailleSG > tailleMaxsg:

                Com = [0]
                while len(Com) < 2:

                    rand = randint(0, len(g.vs()))
                    node = g.vs[rand]

                    if node["name"] in nbComParNoeud.keys():
                        Com = nbComParNoeud[node["name"]]

                    else:
                        continue
                GT = {}
                with open(FileGT, "r") as filee:
                    for indx, line in enumerate(filee):
                        if indx in Com:
                            line = line.rstrip()
                            fields = line.split("\t")
                            noeuds = []
                            for col in fields:
                                noeuds.append(col)
                            GT[indx] = noeuds
                filee.close()

                ndsSG = set()
                for com in Com:
                    temp = [nomIndice[k] for k in GT[com]]
                    ndsSG.update(temp)
                ndsSG.add(node.index)
                tailleSG = len(ndsSG)

                subgraph = g.subgraph(ndsSG)

            try:
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(MaxTimeSec)
                deb = time.time()
                commClus = ChoixAlgo(algo, subgraph, commClus, path, SnapPath)
                fin = time.time()

            except Exception:
                logging.warning('The Algorithm was taking too long on the subgraph num ' + str(
                    i) + '- repetition of the iteration ')
                successful = False

            successful = True

        logging.info("Computation time on the subgraph num " + str(i) + ":" + str(fin - deb))

        if mesure == "FScore":
            somme1 = 0
            somme2 = 0

            # Computation of the mean F-Score for the first loop
            res = Parallel(n_jobs=12)(delayed(loop_FScore_1)(i, GT) for i in commClus.itervalues())
            fscore1 = sum(res) / len(list(GT.itervalues()))

            ##Computation of the mean F-Score for the second loop
            res = Parallel(n_jobs=12)(delayed(loop_FScore_2)(k, GT, commClus) for k in GT.itervalues())
            fscore2 = sum(res) / len(list(GT.itervalues()))

            # Computation of the F-Score on the subgraph
            measure = (fscore1 + fscore2) / 2
            Score = Score + measure
            logging.info('F-Score computed on subgraph num ' + str(i) + ' : ' + str(measure))
            logging.info(str(len(subgraph.vs)) + ' nodes - ' + str(len(subgraph.es)) + ' edges')

        elif mesure == "SimiNbCom":
            simi = 1 - (abs(len(Com) - len(commClus)) / float(2 * len(Com)))
            Score = Score + simi
            logging.info('Accuracy in the number of communities computed on subgraph num ' + str(i) + ' : ' + str(simi))
            logging.info(str(len(subgraph.vs)) + ' nodes - ' + str(len(subgraph.es)) + ' edges')

    end = time.time()
    # Printing of the results
    print("Score global :" + str(Score / nbSG))
    print("temps d'execution :" + str(end - start))
    logging.info("Total computation time :" + str(end - start))
    return Score / nbSG

# Warning : It is possible to get "assertion failed" errors coming from the algorithms.
# For the accuracy in the number of communites, we get negative results to which we add the lowest of the values.
# We thus get postive values that we normalise between 0 and 1.
