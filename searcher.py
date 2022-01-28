from __future__ import print_function
from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.qparser import MultifieldParser
from whoosh import scoring
from query import MyQuery
from query_evaluator import setQueryParser
from movie import Movie

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



def searchIn(corpusDir, query, limit=10, sort=None):
    ix = open_dir(corpusDir)
    searcher = ix.searcher(weighting=scoring.TF_IDF())
    parser = MultifieldParser(["title", "plot"], schema=ix.schema)
    setQueryParser(parser)
    query = parser.parse(query)
    results = searcher.search(query, limit=limit, sortedby=sort)
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
    #print(results1)
    index = 0
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
def toDictionary(results, fun):
    dict = {}
    #print(results)
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


def getMovie(id):
    resultsImdb  = list(searchIn(IMDB_INDEX, "id:\""+id+"\""))
    rImdb = None
    if len(resultsImdb) > 0:
        rImdb = resultsImdb[0]
    imdbMovie = Movie.fromImdb(rImdb)
    #print(imdbMovie)
    
    resultsRotten = list(searchIn(ROTTEN_INDEX, "id:\""+id+"\""))
    rRotten = None
    if len(resultsRotten) > 0:
        rRotten = resultsRotten[0]
    rottenMovie = Movie.fromRotten(rRotten)
    #print("\n", rottenMovie)
    
    resultsWiki = list(searchIn(WIKI_INDEX, "id:\""+id+"\""))
    rWiki = None
    if len(resultsWiki) > 0:
        rWiki = resultsWiki[0]
    wikiMovie = Movie.fromWiki(rWiki)
    #print("\n",wikiMovie)

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
            #print(k1.title, k1.releaseYear, k2.title, k2.releaseYear)
            if k1 == k2:
                #print(k1.title)
                merged.add(Movie.mergeMovies(k1, k2))
    merged = merged.union(set2.difference(set1))
    merged = merged.union(set1.difference(set2))
    
    mapMerged = {}
    for k in merged:
        mapMerged[k] = 0

    return mapMerged

def cutAtRank(map, rank):
    count = 0
    keys = list(map.keys())
    for k in keys:
        if count >= rank:
            map.pop(k)
        count += 1
    return map

def search(rQuery):
    query = MyQuery(rQuery)
    #print(query.getSortedByImdb())
    resultsImdb = searchIn(IMDB_INDEX, query.getImdbQuery(), query.limit, None)
    moviesImdb = toDictionary(resultsImdb, Movie.fromImdb)
    '''
    print("IMDB:")
    for k in moviesImdb.keys():
        print(k.title, moviesImdb[k])
    '''

    resultsRotten = searchIn(ROTTEN_INDEX, query.getRottenQuery(), query.limit, None)
    moviesRotten = toDictionary(resultsRotten, Movie.fromRotten)
    '''
    print("\nROTTEN:")
    for k in moviesRotten.keys():
        print(k.title, moviesRotten[k])
    '''

    merged = mergeMovies(moviesImdb, moviesRotten)

    resultsWiki = searchIn(WIKI_INDEX, query.getWikiQuery(), query.limit, None)
    moviesWiki = toDictionary(resultsWiki, Movie.fromWiki)
    '''
    print("\nWIKI:")
    for k in moviesWiki.keys():
        print(k.title, moviesWiki[k])
    '''

    merged = mergeMovies(merged, moviesWiki)


    '''
    print("\n--Inizio merged--")
    for k in merged.keys():
        print(k.title)
    print("--Fine merged--")
    '''

    if query.sortedBy != None:
        mergedList = list(merged.keys())
        #print(query.sortedBy)
        if query.sortedBy == "releaseYear":
            mergedList = sorted(mergedList, key=(lambda m1 : m1.releaseYear))
        if query.sortedBy == "audienceScore":
            mergedList = sorted(mergedList, key=(lambda m1 : m1.raud), reverse=True)
        if query.sortedBy == "tomatometerScore":
            mergedList = sorted(mergedList, key=(lambda m1 : m1.rcrt), reverse = True)
        if query.sortedBy == "score":
            mergedList = sorted(mergedList, key=(lambda m1 : m1.imdb), reverse = True)
        limit = min(query.limit, len(mergedList))
        return mergedList[0:limit]
    else:
        scores = thresholdMerge(moviesImdb, moviesWiki, query.limit)
        scores = thresholdMerge(scores, moviesRotten, query.limit)
        for k in scores.keys():
            if merged.get(k, -1) != -1:
                merged[k] = scores[k]
        merged = sortDict(merged)
        merged = cutAtRank(merged, query.limit)
 
    return list(merged.keys())
    



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