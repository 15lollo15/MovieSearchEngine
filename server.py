import html
from http.server import BaseHTTPRequestHandler, HTTPServer
from movie import Movie
from searcher import getMovie, search
from urllib.parse import unquote
from htmlBuilder import *

hostName = "localhost"
serverPort = 8080

# TODO: Rigenerare Rotten(questione data)(e anche gli altri) con JAVA
# TODO: Scroll orizzontale (Dark Knight Rises)

class MyServer(BaseHTTPRequestHandler):

    def parsePath(self):
        splitted = self.path.split("?")
        action = splitted[0]
        attr = {}
        if len(splitted) > 1:
            attrString = splitted[1].split("&")
            for a in attrString:
                print("ATTRIBUTO:",a)
                key = a.split("=")[0]
                value = a.split("=")[1].replace("%20", " ")
                attr[key] = value
        return action, attr

    def do_GET(self):
        print(self.path)
        action, attr = self.parsePath()
        str = ""
        content_type = "text/html"
        if action == "/":
            str = MyServer.readTextFile("html/search.html")
        elif action == "/search":
            if len(attr) >= 0 and attr["query"] != "":
                query = html.unescape(unquote(attr["query"].replace("+", " ")))
                print(query)
                if len(query.replace(" ", "")) == 0:
                    self.sendHome()
                    return

                results = search(query)
                str = MyServer.createResultsPage(results)

                str = str.replace(r"%%QUERY%%", query)
            else:
                self.sendHome()
                return
        elif action == "/view":
            if len(attr) >= 0:
                movieId = unquote(attr["movie-id"])
                movie = getMovie(movieId)
                str = MyServer.createViewPage(movie)
        elif action.startswith("/style"):
            str = MyServer.readTextFile(action.removeprefix("/"))
            content_type = "text/css"

        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(bytes(str, "utf-8"))

    def sendHome(self):
        self.send_response(301)
        self.send_header('Location','http://'+hostName+":"+ str(serverPort))
        self.end_headers()

    def replaceCommonTags(htmlString, movie):
        htmlString = htmlString.replace(r"%%TITLE%%", (movie.title))
        htmlString = htmlString.replace(r"%%RELEASE_YEAR%%", movie.releaseYear)

        ratingString = iterToComma(movie.getRating())
        htmlString = htmlString.replace(r"%%RATING%%", ratingString)

        scores = movie.getScores()
        htmlString = htmlString.replace(r"%%RCRT%%", scores["rcrt"])
        htmlString = htmlString.replace(r"%%RAUD%%", scores["raud"])
        htmlString = htmlString.replace(r"%%IMDB%%", scores["imdb"])
        
        genresString = iterToComma(movie.getGenres())
        htmlString = htmlString.replace(r"%%GENRES%%", genresString)

        directorsString = iterToComma(movie.directors)
        print(movie.directors)
        htmlString = htmlString.replace(r"%%DIRECTORS%%", directorsString)
        return htmlString

    def createSingleResult(movie: Movie):
        htmlString = MyServer.readTextFile("html/singleResult.html")
        htmlString = htmlString.replace(r"%%MOVIE_ID%%", movie.id)
        htmlString = MyServer.replaceCommonTags(htmlString, movie)

        return htmlString

    def createResultsPage(results):
        htmlString = MyServer.readTextFile("html/results.html")

        str = ""
        for r in results:
            str += MyServer.createSingleResult(r)
        
        return htmlString.replace(r"%%RESULTS%%", str)


    def createViewPage(movie:Movie):
        htmlString = MyServer.readTextFile("html/viewPage.html");

        htmlString = MyServer.replaceCommonTags(htmlString, movie)

        htmlString = htmlString.replace(r"%%PLOT%%", movie.plot.replace("\n", "<br>"))

        castString = iterToLi(movie.getCast())
        htmlString = htmlString.replace(r"%%CAST%%", castString)
        
        srcs = movie.srcs

        htmlString = MyServer.replaceSrcs(htmlString, srcs, "imdb")
        htmlString = MyServer.replaceSrcs(htmlString, srcs, "rotten")
        htmlString = MyServer.replaceSrcs(htmlString, srcs, "wiki")

        return htmlString

    def replaceSrcs(htmlString, srcs, key):
        src = srcs.get(key, "")
        if src == "":
            htmlString = htmlString.replace(r"%%"+key.upper()+r"_HIDDEN%%", "hidden")
        else:
            htmlString = htmlString.replace(r"%%"+key.upper()+r"_HIDDEN%%", "")
        print(r"%%"+key.upper()+r"_SRC%%")
        htmlString = htmlString.replace(r"%%"+key.upper()+r"_SRC%%", src)
        return htmlString

    def readTextFile(file_path):
        string = ""
        file = open(file_path, "r")
        for line in file:
            string += line
        return string


if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    #webbrowser.open("http://" + hostName + ":" + str(serverPort))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    
    
    webServer.server_close()
    print("Server stopped.")
