# -*- coding: utf-8 -*-
from cgi import print_directory
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
                releaseYear = NUMERIC(stored = True, sortable=True),
                title  = TEXT(stored = True, analyzer = my_analyzer, sortable=True),
                directors = TEXT(stored = True),
                cast = TEXT(stored = True),
                genres = KEYWORD(stored = True, commas=True, scorable=True, lowercase=True),
                src = STORED,
                plot = TEXT(analyzer = my_analyzer),
                fileName = STORED
                )

if not os.path.exists("./wiki_index"):
    os.mkdir("./wiki_index")
ix = create_in("./wiki_index", schema)

writer = ix.writer()

print("Inizio analisi")
PATH = "./corpus/wiki_corpus"
docs_files = os.listdir(PATH)
for doc in docs_files:
    csvFile = open(PATH + "/" + doc, mode="r", encoding="utf-8")
    line = csvFile.readline()
    row = line.split(";;")
    releaseYear = row[0]
    if int(releaseYear) < 1990 or int(releaseYear) > 2015:
        continue
    title = row[1]
    directors = row[3]
    cast = row[4]
    genres = row[5]
    src = row[6]
    plot = row[7].replace("<br>", "\n");
    fileName = PATH + "/" + doc
    print(fileName)
    writer.add_document(
                        id = (releaseYear + " " + html.unescape(title).replace("&", "and")),
                        releaseYear = releaseYear, 
                        title = title, 
                        directors = directors,
                        cast = cast,
                        genres = genres,
                        src = src,
                        plot = plot,
                        fileName = fileName)

print("Fine analisi")
print("Inizio commit")
writer.commit()
print("Fine commit")

