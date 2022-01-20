# -*- coding: utf-8 -*-
from cgi import print_directory
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
                releaseYear = NUMERIC(stored = True),
                title  = TEXT(stored = True, analyzer = my_analyzer),
                origin = STORED,
                directors = TEXT(stored = True),
                cast = TEXT(stored = True),
                genres = KEYWORD(stored = True, commas=True, scorable=True, lowercase=True),
                src = STORED,
                plot = TEXT(analyzer = my_analyzer)
                )

if not os.path.exists("wiki_index"):
    os.mkdir("wiki_index")
ix = create_in("wiki_index", schema)

writer = ix.writer()

csvFile = open("corpus/wiki_corpus_reduced.csv", mode="r", encoding="utf-8")
csv_reader = csv.reader(csvFile, delimiter=",")
line_count = 0
print("Inizio analisi")
for row in csv_reader:
    releaseYear = row[0]
    if int(releaseYear) < 1990 or int(releaseYear) > 2003:
        continue
    title = row[1]
    origin = row[2]
    director = row[3]
    cast = row[4]
    genre = row[5]
    src = row[6]
    plot = row[7]
    writer.add_document(
                        id = (releaseYear + " " + title),
                        releaseYear = releaseYear, 
                        title = title, 
                        origin = origin,
                        director = director,
                        cast = cast,
                        genre = genre,
                        src = src,
                        plot = plot)
    line_count += 1
print("Fine analisi")
print("Inizio commit")
writer.commit()
print("Fine commit")

