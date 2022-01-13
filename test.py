# -*- coding: utf-8 -*-
from cgi import print_directory
from whoosh.index import create_in
from whoosh.fields import *
import os, os.path
import csv
from whoosh.analysis import StemmingAnalyzer

csvFile = open("corpus/wiki_corpus.csv", mode="r", encoding="utf-8")
csv_reader = csv.reader(csvFile, delimiter=",");
line_count = 0
for row in csv_reader:
    releaseYear = row[0]
    title = row[1]
    origin = row[2]
    director = row[3]
    cast = row[4]
    genre = row[5]
    wikiPage = row[6]
    plot = row[7]
    print(plot)
    line_count += 1


