from __future__ import print_function
import imp
from re import I
from unittest import result
from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
from whoosh.qparser import MultifieldParser
import os, os.path
import re
from query_evaluator import setQueryParser

IMDB_INDEX = "imdb_index"
ROTTEN_INDEX = "rotten_index"
WIKI_INDEX = "wiki_index"

# TODO: Da spostare
def sortDict(dict):
    sorted_values = sorted(dict.values(), reverse=True) # Sort the values
    sorted_dict = {}

    for i in sorted_values:
        for k in dict.keys():
            if dict[k] == i and sorted_dict.get(k, -1) == -1:
                sorted_dict[k] = dict[k]
                break
    
    return sorted_dict

def searchIn(corpusDir, queryS, limit=10):
    matchAll = re.search(r"\sALL", str(queryS))
    matchTop = re.search(r"TOP:\d*", str(queryS))
    if matchAll != None:
        limit = None
        queryS = queryS[:-3]
        print(queryS)
    elif matchTop != None:
        print(matchTop)
    
    ix = open_dir(corpusDir)
    searcher = ix.searcher()

    parser = MultifieldParser(["title", "plot"], schema=ix.schema)
    setQueryParser(parser)
    query = parser.parse(queryS)
    results = searcher.search(query, limit=limit)
    return results

# TODO: Riscrivere meglio
def thresholdMerge(results1, results2, k_max = 10):
    scores = {}
    len1 = len(results1)
    len2 = len(results2)
    k = max(len1, len2)
    k = min(k, k_max)
    keys1 = list(results1)
    keys2 = list(results2)
    index = 0
    T = 1000
    for index in range(k):
        T = 0
        if index < len1 :
            key = keys1[index]
            score1 = results1.get(key, 0)
            T += score1
            score2 = results2.get(key, 0)
            if scores.get(key, -1) == -1:
                scores[key] = score1 + score2

        if index < len2 :
            key = keys2[index]
            score2 = results2.get(key, 0)
            T += score2
            score1 = results1.get(key, 0)
            if scores.get(key, -1) == -1:
                scores[key] = score1 + score2
        #print("A", scores)
        t1 = 0
        if index+1 < len1:
            t1 = results1.get(keys1[index+1], 0)

        t2 = 0
        if index+1 < len2:
            t2 = results2.get(keys2[index+1], 0)

        scores = sortDict(scores)
        #print("B", scores)
        T = t1 + t2
        #print(T)
        #print(scores)
        if len(scores) >= k_max :
            s = len(scores) - k_max
            for i in range(s):
                scores.pop(list(scores)[k_max])
        #print(scores)
        count = 0
        for key in scores.keys():
            if scores[key] > T:
                count += 1
        if count == k:
            return scores
    return scores
        

# TODO: Da spostare
def toDictionary(results):
    dict = {}
    for x in results:
        title = x.fields()["title"]
        releaseYear = x.fields()["releaseYear"]
        score = x.score
        key = releaseYear + " " + title
        dict[key] = score
    return dict



print("Imdb results")
resultsImdb = searchIn(IMDB_INDEX,b"score:8")
imdb_dict = toDictionary(resultsImdb)
print(imdb_dict)

print("\nrotten results")
resultsRotten = searchIn(ROTTEN_INDEX,b"genres:horror TOP:20")
rotten_dict = toDictionary(resultsRotten)
print(rotten_dict)

print("\nwiki results")
resultsWiki = searchIn(WIKI_INDEX,b"scream", 5)
wiki_dict = toDictionary(resultsWiki)
print(wiki_dict)

print("\n Merged")
scores = thresholdMerge(imdb_dict, wiki_dict, 10)
scores = thresholdMerge(scores, rotten_dict, 10)
print(scores)

'''
ix = open_dir("imdb_index")
searcher = ix.searcher()
#print(list(searcher.lexicon("plot")))
'''
'''
for t in list(searcher.lexicon("plot")):
    print(t.decode("utf-8"))
'''
'''
parser = QueryParser("plot", schema=ix.schema)
query = parser.parse(b'serial killer')
results = searcher.search(query, limit=20)
if len(results) == 0:
    print("Empty result!!")
else:
    for x in results:
        print(x.fields()["title"])
'''