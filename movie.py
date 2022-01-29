import csv

class Movie:
    def __init__(self, 
                title = "", 
                releaseYear = "",
                origin = "",
                rating = set(), 
                genres = set(), 
                imdb = "",
                raud = "",
                rcrt = "", 
                directors = set(),
                cast = set(),
                plot = "",
                srcs = set()
                ):
        self.title = title
        self.releaseYear = releaseYear
        self.origin = origin
        self.rating = rating
        self.genres = genres
        self.imdb = imdb
        self.raud = raud
        self.rcrt = rcrt
        self.directors = directors
        self.cast = cast
        self.plot = plot
        self.srcs = srcs

    def __eq__(self, __o: object):
        if not isinstance(__o, Movie):
            return False
        movie2 = __o
        #print("Dentro __eq__", movie2.title)
        return self.title == movie2.title and self.releaseYear == movie2.releaseYear

    def __hash__(self):
        return hash((self.releaseYear, self.title))

    def __str__(self):
        str = ""
        str += self.title + "\n"
        str += self.releaseYear + "\n"
        str += self.origin + "\n"
        str += self.rating + "\n"
        str += self.genres.__str__() + "\n"
        str += self.imdb + "\n"
        str += self.raud + "\n"
        str += self.rcrt + "\n"
        str += self.directors.__str__() + "\n"
        str += self.cast.__str__() + "\n"
        str += self.plot + "\n"
        str += self.srcs.__str__() + "\n"
        return str



    def extractPlot(fields, fileName, separator, fieldId):
        corpusIndex = int(fields.get("corpusIndex", ""))
        if(fileName == "corpus/wiki_corpus_reduced.csv"):
            csvFile = open(fileName, mode="r", encoding="utf-8")
            csv_reader = csv.reader(csvFile, delimiter=separator)
            plot = ""
            lc = 0
            for row in csv_reader:
                if lc == corpusIndex:
                    plot = row[fieldId]
                    break
                lc += 1
            return plot
        csvFile = open(fileName, mode="r", encoding="utf-8")
        plot = ""
        lc = 0
        for row in csvFile:
            if lc == corpusIndex:
                plot = row.split(separator)[fieldId]
                break
            lc += 1
        return plot

    def extractSet(fields, fieldName):
        fieldString = fields.get(fieldName, "")
        extractedSet = set()
        if fieldString != "":
            splitted = fieldString.split(",")
            for i in range(len(splitted)):
                extractedSet.add(splitted[i].strip())
        return extractedSet

    def extractCommonFields(fields, fileName, separator, plotFieldId, withPlot=True):
        title = fields.get("title", "")
        releaseYear = fields.get("releaseYear", "")

        directors = Movie.extractSet(fields, "directors")
        cast = Movie.extractSet(fields, "cast")
        genres = Movie.extractSet(fields, "genres")
        
        srcString = fields.get("src", "")
        srcs = set()
        srcs.add(srcString)

        if withPlot:
            plot = Movie.extractPlot(fields, fileName, separator, plotFieldId)
        else:
            plot = ""

        return title, releaseYear, directors, cast, genres, srcs, plot

    def fromWiki(wikiResult, withPlot=True):
        if wikiResult == None:
            return Movie()
        wikiFields = wikiResult.fields()
        origin = wikiFields.get("origin", "")
        title, releaseYear, directors, cast, genres, srcs, plot = Movie.extractCommonFields(wikiFields, 
                                                                                            "corpus/wiki_corpus_reduced.csv",
                                                                                            ",",
                                                                                            7, withPlot)     
        return Movie(title = title, 
                    releaseYear = releaseYear, 
                    origin = origin, 
                    genres= genres,
                    directors = directors,
                    cast = cast,
                    srcs = srcs,
                    plot = plot)

    def fromRotten(rottenResult, withPlot=True):
        if rottenResult == None:
            return Movie()
        rottenFields = rottenResult.fields()
        title, releaseYear, directors, cast, genres, srcs, plot = Movie.extractCommonFields(rottenFields, 
                                                                                            "corpus/rotten_corpus_clean.csv",
                                                                                            ";;",
                                                                                            4, withPlot)     
        raud = rottenFields.get("audienceScore", "")
        rcrt = rottenFields.get("tomatometerScore", "")
        rating = set()
        rating.add(rottenFields.get("rating", ""))
        return Movie(title = title, 
                    releaseYear = releaseYear, 
                    genres = genres,
                    directors = directors,
                    cast = cast,
                    srcs = srcs,
                    plot = plot,
                    raud = raud,
                    rcrt = rcrt,
                    rating = rating)
    
    def fromImdb(imdbResult, withPlot=True):
        if imdbResult == None:
            return Movie()
        #print(imdbResult)
        imdbFields = imdbResult.fields()
        title, releaseYear, directors, cast, genres, srcs, plot = Movie.extractCommonFields(imdbFields, 
                                                                                            "corpus/imdb_corpus_clean.csv",
                                                                                            ";;",
                                                                                            7, withPlot)     
        imdb = imdbFields.get("score", "")
        rating = set()
        rating.add(imdbFields.get("rating", ""))
        return Movie(title = title, 
                    releaseYear = releaseYear, 
                    genres = genres,
                    directors = directors,
                    cast = cast,
                    srcs = srcs,
                    plot = plot,
                    imdb = imdb,
                    rating = rating)

    def returnLonger(str1, str2):
        if len(str1) > len(str2):
            return str1
        return str2

    def mergeMovies(movie1, movie2):
        title = Movie.returnLonger(movie1.title, movie2.title)
        releaseYear = Movie.returnLonger(movie1.releaseYear, movie2.releaseYear)
        origin = Movie.returnLonger(movie1.origin, movie2.origin)
        # TODO: Da capire
        rating = movie1.rating | movie2.rating
        genres = movie1.genres | movie2.genres
        imdb = Movie.returnLonger(movie1.imdb, movie2.imdb)
        raud = Movie.returnLonger(movie1.raud, movie2.raud)
        rcrt = Movie.returnLonger(movie1.rcrt, movie2.rcrt)
        directors = movie1.directors | movie2.directors
        cast = movie1.cast | movie2.cast
        plot = Movie.returnLonger(movie1.plot, movie2.plot)
        srcs = movie1.srcs | movie2.srcs
        return Movie(title, releaseYear, origin, rating, genres, imdb, raud, rcrt, directors, cast, plot, srcs)


    def compareByReleaseYear(m1, m2):
        return m1.releaseYear - m2.releaseYear

    def compareByRaud(m1, m2):
        return m1.raud - m2.raud
    
    def compareByRcrt(m1, m2):
        return m1.rcrt - m2.rcrt

    def compareByImdb(m1, m2):
        return m1.imdb - m2.rcrt