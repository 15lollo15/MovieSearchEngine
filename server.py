import html
from http.server import BaseHTTPRequestHandler, HTTPServer
from venv import create
import webbrowser
from movie import Movie
from searcher import getMovie, search
from urllib.parse import unquote

hostName = "localhost"
serverPort = 8080

# TODO: Plot si vede malissimo
# TODO: Idea triste: JAVA cambia '\n' con '<br>', Pyton cambia '<br>' con '\n'
# TODO: Aggiungere tolower in fase di indexing
# TODO: Query vuota?

class MyServer(BaseHTTPRequestHandler):

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
                str += "<ul>"
                for r in results:
                    str += "<li><a href='view?movie-id=" + r.getId() + "'>" + r.title + "</a></li>"
                str += "</ul>"
            else:
                self.sendHome()
                return
        elif action == "/view":
            if len(attr) >= 0:
                movie = getMovie(attr["movie-id"])
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

    def createViewPage(movie:Movie):
        htmlString = MyServer.readTextFile("html/viewPage.html");
        htmlString = htmlString.replace(r"%%TITLE%%", movie.title)
        htmlString = htmlString.replace(r"%%RELEASE_YEAR%%", movie.releaseYear)

        ratingString = ""
        for r in movie.rating:
            ratingString += r + ", "
        ratingString = ratingString[:-2]
        htmlString = htmlString.replace(r"%%RATING%%", ratingString)

        htmlString = htmlString.replace(r"%%RCRT%%", movie.rcrt)
        htmlString = htmlString.replace(r"%%RAUD%%", movie.raud)
        htmlString = htmlString.replace(r"%%IMDB%%", movie.imdb)
        
        genresString = ""
        for g in movie.genres:
            genresString += g + ", "
        genresString = genresString[:-2]
        htmlString = htmlString.replace(r"%%GENRES%%", genresString)

        directorsString = ""
        for d in movie.directors:
            directorsString += d + ", "
        directorsString = directorsString[:-2]
        htmlString = htmlString.replace(r"%%DIRECTORS%%", directorsString)

        htmlString = htmlString.replace(r"%%PLOT%%", movie.plot)

        castString = ""
        for c in movie.cast:
            castString += c + ", "
        castString = castString[:-2]
        htmlString = htmlString.replace(r"%%CAST%%", castString)

        htmlString = htmlString.replace(r"%%IMDB_SRC%%", movie.srcs.get("imdb", ""))
        htmlString = htmlString.replace(r"%%ROTTEN_SRC%%", movie.srcs.get("rotten", ""))
        htmlString = htmlString.replace(r"%%WIKI_SRC%%", movie.srcs.get("wiki", ""))

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
