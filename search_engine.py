from searcher import search, getMovie
import webbrowser

# TODO: \n in IMDb

def viewResults(results):
    print("Results:")
    if len(results) == 0:
        print("No results for your query")
        return
    lc = 1
    for k in results.keys():
        print("[" + str(lc) + "]\t" + k)
        lc += 1

def showInBrowser(movie):
    htmlFile = open("tmpHtml.html", "w")
    htmlFile.write("<html>")
    htmlFile.write("<head></head>")
    htmlFile.write("<body>")
    htmlFile.write("<h1>" + movie.title + "</h1")
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
        movieID = list(movies.keys())[index-1]
        movie = getMovie(movieID)
        showInBrowser(movie)

