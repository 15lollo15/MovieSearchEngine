import csv

class Movie:
    def __init__(self,
                id = "", 
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
                srcs = {}
                ):
        self.id = id
        self.title = title
        self.releaseYear = releaseYear
        self.origin = origin
        self.rating = rating
        if "NC" in self.rating:
            self.rating.remove("NC")
        self.genres = genres
        self.imdb = imdb
        self.raud = raud
        self.rcrt = rcrt
        self.directors = directors
        self.cast = cast
        self.plot = plot
        self.srcs = srcs

    def returnDefaultSet(set):
        if len(set) == 0:
            return {'-'}
        return set

    def getRating(self):
        return Movie.returnDefaultSet(self.rating)

    def getGenres(self):
        return Movie.returnDefaultSet(self.genres)

    def returnDefaultValue(str):
        if str == "":
            return "-"
        return str

    def getCast(self):
        return Movie.returnDefaultSet(self.cast)

    def getScores(self):
        map = {}
        map["imdb"] = Movie.returnDefaultValue(self.imdb)
        map["raud"] = Movie.returnDefaultValue(self.raud)
        map["rcrt"] = Movie.returnDefaultValue(self.rcrt)
        return map

    def __eq__(self, __o: object):
        if not isinstance(__o, Movie):
            return False
        movie2 = __o
        #print("Dentro __eq__", movie2.title)
        return self.id == movie2.id

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        str = ""
        str += self.id + "\n"
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

    def extractPlot(fields, fieldId):
        fileName = fields.get("fileName")
        csvFile = open(fileName, mode="r", encoding="utf-8")
        line = csvFile.readline()
        row = line.split(";;")
        return row[fieldId]

    def extractSet(fields, fieldName):
        fieldString = fields.get(fieldName, "")
        extractedSet = set()
        if fieldString != "":
            splitted = fieldString.split(",")
            for i in range(len(splitted)):
                extractedSet.add(splitted[i].strip())
        return extractedSet

    def extractCommonFields(fields, plotFieldId, srcName, withPlot=True):
        id = fields.get("id","")
        title = fields.get("title", "")
        releaseYear = fields.get("releaseYear", "")

        directors = Movie.extractSet(fields, "directors")
        cast = Movie.extractSet(fields, "cast")
        genres = Movie.extractSet(fields, "genres")
        
        srcString = fields.get("src", "")
        srcs = {srcName : srcString}

        if withPlot:
            plot = Movie.extractPlot(fields, plotFieldId)
        else:
            plot = ""

        return id, title, releaseYear, directors, cast, genres, srcs, plot

    def fromWiki(wikiResult, withPlot=True):
        if wikiResult == None:
            return Movie()
        wikiFields = wikiResult.fields()
        origin = wikiFields.get("origin", "")
        id, title, releaseYear, directors, cast, genres, srcs, plot = Movie.extractCommonFields(wikiFields,
                                                                                            7, "wiki", withPlot)     
        return Movie(id = id,
                    title = title, 
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
        id, title, releaseYear, directors, cast, genres, srcs, plot = Movie.extractCommonFields(rottenFields, 
                                                                                            4, "rotten", withPlot)     
        raud = rottenFields.get("audienceScore", "")
        rcrt = rottenFields.get("tomatometerScore", "")
        rating = set()
        rating.add(rottenFields.get("rating", ""))
        return Movie(id = id,
                    title = title, 
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
        id, title, releaseYear, directors, cast, genres, srcs, plot = Movie.extractCommonFields(imdbFields, 
                                                                                            7, "imdb", withPlot)     
        imdb = imdbFields.get("score", "")
        rating = set()
        rating.add(imdbFields.get("rating", ""))
        return Movie(id = id,
                    title = title, 
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
        id = movie1.id
        title = Movie.returnLonger(movie1.title, movie2.title)
        releaseYear = Movie.returnLonger(movie1.releaseYear, movie2.releaseYear)
        origin = Movie.returnLonger(movie1.origin, movie2.origin)
        # TODO: Da capire
        rating = movie1.rating | movie2.rating
        genres = {x.lower() for x in movie1.genres} | {x.lower() for x in movie2.genres}
        imdb = Movie.returnLonger(movie1.imdb, movie2.imdb)
        raud = Movie.returnLonger(movie1.raud, movie2.raud)
        rcrt = Movie.returnLonger(movie1.rcrt, movie2.rcrt)
        directors = movie1.directors | movie2.directors
        cast = movie1.cast | movie2.cast
        plot = Movie.returnLonger(movie1.plot, movie2.plot)
        srcs = movie1.srcs | movie2.srcs
        return Movie(id, title, releaseYear, origin, rating, genres, imdb, raud, rcrt, directors, cast, plot, srcs)


    def compareByReleaseYear(m1, m2):
        return m1.releaseYear - m2.releaseYear

    def compareByRaud(m1, m2):
        return m1.raud - m2.raud
    
    def compareByRcrt(m1, m2):
        return m1.rcrt - m2.rcrt

    def compareByImdb(m1, m2):
        return m1.imdb - m2.rcrt