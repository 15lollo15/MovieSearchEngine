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

schema = Schema(
                title = ID(stored = True),
                releaseYear = ID(stored= True),
                rating = TEXT(stored = True),
                genres = KEYWORD(stored = True, commas = True),
                score = NUMERIC(stored = True, numtype=float),
                directors = KEYWORD(stored = True, commas = True),
                cast = KEYWORD(stored = True, commas = True),
                plot = TEXT(analyzer = my_analyzer)
                )

if not os.path.exists("imdb_index"):
    os.mkdir("imdb_index")
ix = create_in("imdb_index", schema)

writer = ix.writer()

csvFile = open("corpus/imdb_corpus.csv", mode="r", encoding="utf-8")
line_count = 0
print("Inizio analisi")
for line in csvFile:
    print(line_count)
    row = line.split(";;")
    title = row[0]
    releaseYear = row[1]
    rating = row[2]
    genres = row[3]
    score = row[4]
    directors = row[5]
    cast = row[6]
    plot = row[7]

    writer.add_document(
                        title = title,
                        releaseYear = releaseYear,
                        rating = rating,
                        genres = genres,
                        score = score,
                        directors = directors,
                        cast = cast,
                        plot = plot
                        )
    line_count += 1
print("Fine analisi")
print("Inizio commit")
writer.commit()
print("Fine commit")