# -*- coding: utf-8 -*-
from cgi import print_directory
from turtle import title
from whoosh.index import create_in
from whoosh.fields import *
import os, os.path
import csv
from whoosh.analysis import StemmingAnalyzer, CharsetFilter
from whoosh.support.charset import default_charset, charset_table_to_dict

charmap = charset_table_to_dict(default_charset)
my_analyzer = StemmingAnalyzer() | CharsetFilter(charmap)

schema = Schema(id = ID(stored=True),
                title = TEXT(analyzer = my_analyzer, stored = True, sortable=True),
                audienceScore = NUMERIC(stored = True, sortable=True),
                tomatometerScore = NUMERIC(stored = True, sortable=True),
                rating = TEXT(stored = True),
                plot = TEXT(analyzer = my_analyzer),
                genres = KEYWORD(stored = True, commas = True, scorable=True, lowercase=True),
                directors = TEXT(stored = True),
                releaseYear = NUMERIC(stored = True, sortable=True),
                cast = TEXT(stored = True),
                src = STORED,
                fileName = STORED
                )

if not os.path.exists("rotten_index"):
    os.mkdir("rotten_index")
ix = create_in("rotten_index", schema)

writer = ix.writer()

PATH = "corpus/rotten_corpus"
print("Inizio analisi")
docs_files = os.listdir(PATH)
for doc in docs_files:
    csvFile = open(PATH + "/" +doc, mode="r", encoding="utf8")
    line = csvFile.readline()
    row = line.split(";;")
    title = row[0]
    audienceScore = row[1]
    if audienceScore == "":
        audienceScore = -1
    tomatometerScore = row[2]
    if tomatometerScore == "":
        tomatometerScore = -1
    rating = row[3]
    plot = row[4]
    genres = row[5]
    directors = row[6]
    releaseYear = row[7]
    cast = row[8]
    src = row[9].replace("\n", "")
    fileName = PATH + "/" +doc
    print(doc)

    writer.add_document(
                        id = (releaseYear + " " + title),
                        title = title,
                        audienceScore = audienceScore,
                        tomatometerScore = tomatometerScore,
                        rating = rating,
                        plot = plot,
                        genres = genres,
                        directors = directors,
                        releaseYear = releaseYear,
                        cast = cast,
                        src = src,
                        fileName = fileName
                        )

print("Fine analisi")
print("Inizio commit")
writer.commit()
print("Fine commit")