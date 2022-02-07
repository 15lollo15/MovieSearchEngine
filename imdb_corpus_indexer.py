# -*- coding: utf-8 -*-
import html
from whoosh.index import create_in
from whoosh.fields import *
import os, os.path
import csv
from whoosh.analysis import StemmingAnalyzer, CharsetFilter
from whoosh.support.charset import default_charset, charset_table_to_dict

charmap = charset_table_to_dict(default_charset)
my_analyzer = StemmingAnalyzer() | CharsetFilter(charmap)

schema = Schema(
                id = ID(stored = True),
                title = TEXT(analyzer = my_analyzer, stored = True, sortable=True),
                releaseYear = NUMERIC(stored= True, sortable=True),
                rating = TEXT(stored = True),
                genres = KEYWORD(stored = True, commas = True, scorable=True, lowercase=True),
                score = NUMERIC(stored = True, numtype=int, sortable=True),
                directors = TEXT(stored = True),
                cast = TEXT(stored = True),
                plot = TEXT(analyzer = my_analyzer),
                src = STORED,
                fileName = STORED
                )

if not os.path.exists("imdb_index"):
    os.mkdir("imdb_index")
ix = create_in("imdb_index", schema)
writer = ix.writer()

print("Inizio analisi")
PATH = "corpus/imdb_corpus"
docs_files = os.listdir(PATH)
for doc in docs_files:
    csvFile = open(PATH + "/" + doc, mode="r", encoding="utf-8")
    line = csvFile.readline()
    row = line.split(";;")
    title = row[0]
    releaseYear = row[1]
    rating = row[2]
    genres = row[3]
    score = str(round(float(row[4])))
    directors = row[5]
    cast = row[6]
    plot = row[7].replace("<br>","\n")
    src = row[8]
    fileName = PATH + "/" + doc
    print(fileName)
    writer.add_document(
                        id = (releaseYear + " " + html.unescape(title).replace("&", "and")),
                        title = title,
                        releaseYear = releaseYear,
                        rating = rating,
                        genres = genres,
                        score = score,
                        directors = directors,
                        cast = cast,
                        plot = plot,
                        src = src,
                        fileName = fileName
                        )

print("Fine analisi")
print("Inizio commit")
writer.commit()
print("Fine commit")