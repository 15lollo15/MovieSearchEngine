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
                releaseYear = NUMERIC(stored = True, sortable=True),
                title  = TEXT(stored = True, analyzer = my_analyzer, sortable=True),
                origin = STORED,
                directors = TEXT(stored = True),
                cast = TEXT(stored = True),
                genres = KEYWORD(stored = True, commas=True, scorable=True, lowercase=True),
                src = STORED,
                plot = TEXT(analyzer = my_analyzer),
                corpusIndex = STORED
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
        line_count += 1
        continue
    title = row[1]
    origin = row[2]
    directors = row[3]
    cast = row[4]
    genres = row[5]
    src = row[6]
    plot = row[7]
    corpusIndex = str(line_count)
    writer.add_document(
                        id = (releaseYear + " " + title),
                        releaseYear = releaseYear, 
                        title = title, 
                        origin = origin,
                        directors = directors,
                        cast = cast,
                        genres = genres,
                        src = src,
                        plot = plot,
                        corpusIndex = corpusIndex)
    line_count += 1
print("Fine analisi")
print("Inizio commit")
writer.commit()
print("Fine commit")

