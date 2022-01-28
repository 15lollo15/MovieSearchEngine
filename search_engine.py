from searcher import search, getMovie
import webbrowser
import re

# TODO: \n in IMDb

def viewResults(results):
    print("Results:")
    if len(results) == 0:
        print("No results for your query")
        return
    lc = 1
    for k in results:
        print("[" + str(lc) + "]\t" + k.title + "\t" + str(k.releaseYear))
        lc += 1

def showInBrowser(movie):
    htmlFile = open("tmpHtml.html", "w")
    htmlFile.write("<html>")
    htmlFile.write("<head></head>")
    htmlFile.write("<body>")
    htmlFile.write("<h1>" + movie.title + "</h1>")
    htmlFile.write("<p>" + re.sub("\. ", ".<br>", movie.plot) + "</p>")
    htmlFile.write("</body>")
    htmlFile.write("</html>")
    htmlFile.close()
    webbrowser.open("tmpHtml.html")

q = input("Query: ")
movies = search(q)
viewResults(movies)

if len(movies) > 0:
    index = input("Show result('n' none): ")
    if index != 'n':
        index = int(index)
        movie = movies[index-1]
        movie = getMovie(str(movie.releaseYear) + " " + movie.title)
        showInBrowser(movie)

