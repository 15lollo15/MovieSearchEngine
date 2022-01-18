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
                title = TEXT(stored = True),
                audienceScore = NUMERIC(stored = True),
                tomatometerScore = NUMERIC(stored = True),
                rating = TEXT(stored = True),
                plot = TEXT(analyzer = my_analyzer),
                genres = KEYWORD(stored = True, commas = True),
                directors = KEYWORD(stored = True, commas = True),
                releaseYear = NUMERIC(stored = True),
                cast = KEYWORD(stored = True, commas=True)
                )

if not os.path.exists("rotten_index"):
    os.mkdir("rotten_index")
ix = create_in("rotten_index", schema)

writer = ix.writer()

csvFile = open("corpus/rotten_corpus_clean.csv", mode="r", encoding="utf-8")
line_count = 0
print("Inizio analisi")
for line in csvFile:
    if line_count >= 1000:
        break;
    print(line_count)
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
    print(audienceScore, tomatometerScore, releaseYear)
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
                        cast = cast
                        )
    line_count += 1
print("Fine analisi")
print("Inizio commit")
writer.commit()
print("Fine commit")