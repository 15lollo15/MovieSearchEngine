import html
from http.server import BaseHTTPRequestHandler, HTTPServer
import webbrowser
from typedef.movie import Movie
from searcher import getMovie, search
from urllib.parse import unquote
from htmlBuilder import *

hostName = "localhost"
serverPort = 8080

# TODO: Refactor
# TODO: Benchmark
# TODO: Presentazione
# TODO: Debian/MAC compatible
# TODO: Index ALL (forse)
# TODO: Fix page 10 

class MyServer(BaseHTTPRequestHandler):

    MAX_RESULTS = 10
    MAX_PAGE = 10

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

                if len(results) >= MyServer.MAX_RESULTS:
                    max_page = int(len(results)/MyServer.MAX_RESULTS)
                else:
                    max_page = 1
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
                movie = getMovie(movieId, withPlot=True)
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

    def createSingleResult(movie: Movie):
        htmlString = MyServer.readTextFile("html/singleResult.html")
        htmlString = htmlString.replace(r"%%MOVIE_ID%%", movie.id)
        htmlString = replaceCommonTags(htmlString, movie)

        return htmlString

    def createPageForm(p, currentPage = False):
        htmlString = MyServer.readTextFile("html/pageform.html")
        htmlString = htmlString.replace(r"%%PAGE%%", str(p))
        if currentPage:
            htmlString = htmlString.replace(r"%%CURRENT_PAGE%%", "currentPage")
        else:
            htmlString = htmlString.replace(r"%%CURRENT_PAGE%%", "")
        return htmlString

    def getFirstPage(p = 1, max_page = 1):
        fp = 1
        lastBlock = (max_page - MyServer.MAX_PAGE/2)
        if p > (MyServer.MAX_PAGE/2):
            if p >= lastBlock:
                fp = max_page - MyServer.MAX_PAGE + 1
            else:
                fp += p - (MyServer.MAX_PAGE/2)
        return int(fp)
        

    def createPageSelector(htmlString, p = 1, max_page = 1):
        fp = MyServer.getFirstPage(p, max_page)

        if p == 1:
            htmlString = htmlString.replace(r"%%HIDDEN_PREV%%", "hidden")
        else:
            htmlString = htmlString.replace(r"%%PREV_PAGE%%", str(p-1))
        
        if p == max_page:
            htmlString = htmlString.replace(r"%%HIDDEN_NEXT%%", "hidden")
        else:
            htmlString = htmlString.replace(r"%%NEXT_PAGE%%", str(p+1))
        
        pagesString = ""
        if p != max_page:
            for i in range(fp, min(max_page+1,fp+MyServer.MAX_PAGE)):
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

        if len(results) == 0:
            string = "Not found"
        
        htmlString =  htmlString.replace(r"%%RESULTS%%", string)
        htmlString = MyServer.createPageSelector(htmlString, p, max_page)
        
        return htmlString


    def createViewPage(movie:Movie):
        htmlString = MyServer.readTextFile("html/viewPage.html");

        htmlString = replaceCommonTags(htmlString, movie)

        htmlString = htmlString.replace(r"%%PLOT%%", movie.plot.replace("\n", "<br>"))

        castString = iterToLi(movie.getCast())
        htmlString = htmlString.replace(r"%%CAST%%", castString)
        
        srcs = movie.srcs

        htmlString = replaceSrcs(htmlString, srcs, "imdb")
        htmlString = replaceSrcs(htmlString, srcs, "rotten")
        htmlString = replaceSrcs(htmlString, srcs, "wiki")

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
    webbrowser.open("http://" + hostName + ":" + str(serverPort))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    
    
    webServer.server_close()
    print("Server stopped.")
