from whoosh.index import open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser
import os, os.path

ix = open_dir("wiki_index")
searcher = ix.searcher()
#print(list(searcher.lexicon("plot")))

for t in list(searcher.lexicon("plot")):
    print(t.decode("utf-8"))


parser = QueryParser("plot", schema=ix.schema)
query = parser.parse(b'\xe8\xa3\x95\xe4\xbb\x81')
results = searcher.search(query, limit=20)
if len(results) == 0:
    print("Empty result!!")
else:
    for x in results:
        print(x.fields()["title"])
        