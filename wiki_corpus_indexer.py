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

schema = Schema(releaseYear = ID(stored = True),
                title  = ID(stored = True),
                origin = STORED,
                director = TEXT(stored = True),
                cast = TEXT(stored = True),
                genre = TEXT(stored = True),
                wikiPage = STORED,
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
    title = row[1]
    origin = row[2]
    director = row[3]
    cast = row[4]
    genre = row[5]
    wikiPage = row[6]
    plot = row[7]
    writer.add_document(releaseYear = releaseYear, 
                        title = title, 
                        origin = origin,
                        director = director,
                        cast = cast,
                        genre = genre,
                        wikiPage = wikiPage,
                        plot = plot)
    line_count += 1
print("Fine analisi")
print("Inizio commit")
writer.commit()
print("Fine commit")

