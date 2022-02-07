import html
from http.server import BaseHTTPRequestHandler, HTTPServer
from movie import Movie
from searcher import getMovie, search
from urllib.parse import unquote
from htmlBuilder import *

hostName = "localhost"
serverPort = 8080


class MyServer(BaseHTTPRequestHandler):

    MAX_RESULTS = 10

    def parsePath(self):
        splitted = self.path.split("?")
        action = splitted[0]
        attr = {}
        if len(splitted) > 1:
            attrString = splitted[1].split("&")
            for a in attrString:
                key = a.split("=")[0]
                value = a.split("=")[1].replace("%20", " ")
                attr[key] = value
        return action, attr

    def do_GET(self):
        action, attr = self.parsePath()
        str = ""
        content_type = "text/html"
        if action == "/":
            str = MyServer.readTextFile("html/search.html")
        elif action == "/search":
            if len(attr) >= 0 and attr["query"] != "":
                query = html.unescape(unquote(attr["query"].replace("+", " ")))
                if len(query.replace(" ", "")) == 0:
                    self.sendHome()
                    return

                results = search(query)
                page = 1
                if attr.get("p", None) != None and attr["p"] != "":
                    try:
                        page = int(attr["p"])
                    except ValueError:
                        page = 1

                if page < 1:
                    page = 1

                max_page = int(len(results)/MyServer.MAX_RESULTS)
                if  page > max_page:
                    page = max_page
                results = results[(page-1)*MyServer.MAX_RESULTS:((page-1)*MyServer.MAX_RESULTS)+MyServer.MAX_RESULTS]
                str = MyServer.createResultsPage(results, page, max_page)

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
        htmlString = htmlString.replace(r"%%DIRECTORS%%", directorsString)
        return htmlString

    def createSingleResult(movie: Movie):
        htmlString = MyServer.readTextFile("html/singleResult.html")
        htmlString = htmlString.replace(r"%%MOVIE_ID%%", movie.id)
        htmlString = MyServer.replaceCommonTags(htmlString, movie)

        return htmlString

    def createPageForm(p, currentPage = False):
        htmlString = MyServer.readTextFile("html/pageform.html")
        htmlString = htmlString.replace(r"%%PAGE%%", str(p))
        if currentPage:
            htmlString = htmlString.replace(r"%%CURRENT_PAGE%%", "currentPage")
        else:
            htmlString = htmlString.replace(r"%%CURRENT_PAGE%%", "")
        return htmlString

    def createPageSelector(htmlString, p = 1, max_page = 1):
        if p == 1:
            htmlString = htmlString.replace(r"%%HIDDEN_PREV%%", "hidden")
        else:
            htmlString = htmlString.replace(r"%%PREV_PAGE%%", str(p-1))
        
        if p == max_page:
            htmlString = htmlString.replace(r"%%HIDDEN_NEXT%%", "hidden")
        else:
            htmlString = htmlString.replace(r"%%NEXT_PAGE%%", str(p+1))
        
        pagesString = ""
        for i in range(1, max_page+1):
            currentPage = False
            if i == p:
                currentPage = True
            pagesString += MyServer.createPageForm(i, currentPage)
        return htmlString.replace(r"%%PAGES%%", pagesString)

    def createResultsPage(results, p = 1, max_page = 1):
        htmlString = MyServer.readTextFile("html/results.html")

        string = ""
        for r in results:
            string += MyServer.createSingleResult(r)
        
        htmlString =  htmlString.replace(r"%%RESULTS%%", string)
        htmlString = MyServer.createPageSelector(htmlString, p, max_page)
        
        return htmlString


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
