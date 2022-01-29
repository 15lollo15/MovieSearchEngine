import html
from http.server import BaseHTTPRequestHandler, HTTPServer
import webbrowser
from searcher import getMovie, search

hostName = "localhost"
serverPort = 8080

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
            if len(attr) >= 0:
                results = search(attr["query"])
                str += "<ul>"
                for r in results:
                    str += "<li><a href='view?movie-id=" + r.getId() + "'>" + r.title + "</a></li>"
                str += "</ul>"
        elif action == "/view":
            if len(attr) >= 0:
                movie = getMovie(attr["movie-id"])
                str += "<h1>" + movie.title + "</h1>"
                str += "<span>" + movie.plot + "</span>"
        elif action.startswith("/style"):
            str = MyServer.readTextFile(action.removeprefix("/"))
            content_type = "text/css"

        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(bytes(str, "utf-8"))

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
