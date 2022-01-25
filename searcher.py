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
        movie = fun(x)
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
    resultsImdb  = list(searchIn(IMDB_INDEX, "id:\""+id+"\"")[0])
    rImdb = None
    if len(resultsImdb) > 0:
        rImdb = resultsImdb[0]
    imdbMovie = Movie.fromImdb(rImdb)
    #print(imdbMovie)
    
    resultsRotten = list(searchIn(ROTTEN_INDEX, "id:\""+id+"\"")[0])
    rRotten = None
    if len(resultsRotten) > 0:
        rRotten = resultsRotten[0]
    rottenMovie = Movie.fromRotten(rRotten)
    #print("\n", rottenMovie)
    
    resultsWiki = list(searchIn(WIKI_INDEX, "id:\""+id+"\"")[0])
    rWiki = None
    if len(resultsWiki) > 0:
        rWiki = resultsWiki[0]
    wikiMovie = Movie.fromWiki(rWiki)
    #print("\n",wikiMovie)

    if imdbMovie == None and rottenMovie == None and wikiMovie == None:
        return None
    
    mergedMovie = Movie.mergeMovies(Movie.mergeMovies(imdbMovie, rottenMovie), wikiMovie)
    return mergedMovie
    
def search(rQuery):
    query = MyQuery(rQuery)
    resultsImdb = searchIn(IMDB_INDEX, query.getImdbQuery(), query.limit, query.sortedBy)
    moviesImdb = toDictionary(resultsImdb, Movie.fromImdb)
    print("IMDB:")
    for k in moviesImdb.keys():
        print(k.title, moviesImdb[k])

    resultsRotten = searchIn(ROTTEN_INDEX, query.getRottenQuery(), query.limit, query.sortedBy)
    moviesRotten = toDictionary(resultsRotten, Movie.fromRotten)
    print("\nROTTEN:")
    for k in moviesRotten.keys():
        print(k.title, moviesRotten[k])

    resultsWiki = searchIn(WIKI_INDEX, query.getWikiQuery(), query.limit, query.sortedBy)
    moviesWiki = toDictionary(resultsWiki, Movie.fromWiki)
    print("\nWIKI:")
    for k in moviesWiki.keys():
        print(k.title, moviesWiki[k])


    if(query.sortedBy != None):
        pass
    else:
        scores = thresholdMerge(moviesImdb, moviesWiki, query.limit)
        scores = thresholdMerge(scores, moviesRotten, query.limit)
    return scores


scores = search("spider-man")
print("\n")
for k in scores.keys():
    print(k.title, scores[k])

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