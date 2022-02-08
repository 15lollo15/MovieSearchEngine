from os import kill
from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.qparser import MultifieldParser
from whoosh.qparser import GtLtPlugin
from whoosh import qparser
from typedef.movie import Movie
from typedef.query import MyQuery

IMDB_INDEX = "imdb_index"
ROTTEN_INDEX = "rotten_index"
WIKI_INDEX = "wiki_index"

def setQueryParser(qp):
    qp.replace_plugin(GtLtPlugin())
    qp.remove_plugin_class(qparser.WildcardPlugin)

def sortDict(dict):
    sorted_values = sorted(dict.values(), reverse=True) # Sort the values
    sorted_dict = {}

    for i in sorted_values:
        for k in dict.keys():
            if dict[k] == i and sorted_dict.get(k, -1) == -1:
                sorted_dict[k] = dict[k]
                break
    
    return sorted_dict

def searchIn(corpusDir, query, limit=10, sort=None):
    ix = open_dir(corpusDir)
    searcher = ix.searcher()
    parser = MultifieldParser(["title", "plot"], schema=ix.schema)
    setQueryParser(parser)
    query = parser.parse(query)
    results = searcher.search(query, limit=limit, sortedby=sort)
    return results

def getScore(index, results1, results2, scores:dict, killAloneResult = False):
    len1 = len(results1)
    keys1 = list(results1)
    T = 0
    if index < len1 :
        key = keys1[index]
        score1 = results1.get(key, 0)
        T = score1
        score2 = results2.get(key, 0)
        if scores.get(key, -1) == -1:
            scores[key] = score1 + score2


def getThreshold(index, results1):
    keys1 = list(results1)
    if index+1 < len(results1):
        return results1.get(keys1[index+1], 0)
    return 0

def cleanScores(scores, k_max):
    if len(scores) >= k_max :
        s = len(scores) - k_max
        for i in range(s):
            scores.pop(list(scores)[k_max])

def countValidScores(scores, T):
    count = 0
    for key in scores.keys():
        if scores[key] > T:
            count += 1
    return count

def thresholdMerge(results1:dict, results2:dict, k_max = 10, killAloneResult = False):
    scores = {}
    len1 = len(results1)
    len2 = len(results2)

    if k_max == None:
        k_max = len1 + len2
    
    k = max(len1, len2)
    k = min(k, k_max)
    
    keys = list(results1.keys())
    for ki in keys:
        if results2.get(ki, None) == None:
            results1.pop(ki)

    keys = list(results2.keys())
    for ki in keys:
        if results1.get(ki, None) == None:
            results2.pop(ki)

    index = 0
    for index in range(k):
        getScore(index, results1, results2, scores)
        getScore(index, results2, results1, scores)

        t1 = getThreshold(index, results1)
        t2 = getThreshold(index, results2)
        T = t1 + t2
        scores = sortDict(scores)
        cleanScores(scores, k_max)
        count = countValidScores(scores, T)
        if count == k:
            return scores
    return scores
        
def toDictionary(results, fun):
    dict = {}
    for x in results:
        movie = fun(x, False)
        dict[movie] = x.score
    return dict

def extractField(movie, fieldName):
    field = ""
    if(movie != None):
        field = movie.fields().get(fieldName, "")
    return field

def selectField(movies, fieldname):
    candidateField = []
    for m in movies:
        if m != None:
            candidateField.append(extractField(m, fieldname))
    for f in candidateField:
        if f != "":
            return f
    return ""


def getMovieFrom(index, id, extractFunction, withPlot = False):
    results  = list(searchIn(index, "id:\""+id+"\""))
    r = None
    if len(results) > 0:
        r = results[0]
    movie = extractFunction(r, withPlot)
    return movie

def getMovie(id, withPlot = False):
    imdbMovie  = getMovieFrom(IMDB_INDEX, id, Movie.fromImdb, withPlot)
    rottenMovie = getMovieFrom(ROTTEN_INDEX, id, Movie.fromRotten, withPlot)
    wikiMovie = getMovieFrom(WIKI_INDEX, id, Movie.fromWiki, withPlot)

    if imdbMovie == None and rottenMovie == None and wikiMovie == None:
        return None
    
    mergedMovie = Movie.mergeMovies(Movie.mergeMovies(imdbMovie, rottenMovie), wikiMovie)
    return mergedMovie

def mergeMovies(movies1, movies2):
    set1 = set()
    for k in movies1.keys():
        set1.add(k)
    
    set2 = set()
    for k in movies2.keys():
        set2.add(k)

    merged = set()
    for k1 in set1:
        for k2 in set2:
            if k1 == k2:
                merged.add(Movie.mergeMovies(k1, k2))
    merged = merged.union(set2.difference(set1))
    merged = merged.union(set1.difference(set2))
    
    mapMerged = {}
    for k in merged:
        mapMerged[k] = 0

    return mapMerged

def cutAtRank(map, rank):
    if rank == None:
        rank = len(map.keys())
    count = 0
    keys = list(map.keys())
    for k in keys:
        if count >= rank:
            map.pop(k)
        count += 1
    return map

def search(rQuery):
    query = MyQuery(rQuery)

    resultsImdb = searchIn(IMDB_INDEX, query.getImdbQuery(), None, None)
    moviesImdb = toDictionary(resultsImdb, Movie.fromImdb)
     
    resultsRotten = searchIn(ROTTEN_INDEX, query.getRottenQuery(), None, None)
    moviesRotten = toDictionary(resultsRotten, Movie.fromRotten)
  
    merged = mergeMovies(moviesImdb, moviesRotten)

    resultsWiki = searchIn(WIKI_INDEX, query.getWikiQuery(), None, None)
    moviesWiki = toDictionary(resultsWiki, Movie.fromWiki)

    merged = mergeMovies(merged, moviesWiki)
    if query.sortedBy != None:
        mergedList = list(merged.keys())
        if query.sortedBy == "releaseYear":
            mergedList = sorted(mergedList, key=(lambda m1 : m1.releaseYear))
        if query.sortedBy == "audienceScore":
            mergedList = sorted(mergedList, key=(lambda m1 : m1.raud), reverse=True)
        if query.sortedBy == "tomatometerScore":
            mergedList = sorted(mergedList, key=(lambda m1 : m1.rcrt), reverse = True)
        if query.sortedBy == "score":
            mergedList = sorted(mergedList, key=(lambda m1 : m1.imdb), reverse = True)
        limit = min(query.limit, len(mergedList))
        merged = mergedList[0:limit]
    else:
        sortDict(moviesImdb)
        sortDict(moviesRotten)
        sortDict(moviesWiki)
        scores = thresholdMerge(moviesImdb, moviesWiki, query.limit)
        scores = thresholdMerge(scores, moviesRotten, query.limit)
        for k in scores.keys():
            if merged.get(k, -1) != -1:
                merged[k] = scores[k]
        merged = sortDict(merged)
        merged = cutAtRank(merged, query.limit)
        merged = list(merged.keys())
    
    L = merged

    return L


