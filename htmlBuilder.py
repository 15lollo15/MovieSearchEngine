def iterToComma(iter):
    '''Converts iterable into a string comma separated'''
    string = ""
    for x in iter:
        string += x + ", "
    string = string[:-2]
    return string

def iterToLi(iter):
    '''Converts iterable into a string containg html list item'''
    string = ""
    for x in iter:
        string += "<li>" + x + "</li>"
    string = string[:-2]
    return string

def replaceCommonTags(htmlString, movie):
    '''Replaces the fields in marked places'''
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

def replaceSrcs(htmlString, srcs, key):
    '''Makes src visible if is not "", not visible otherwise'''
    src = srcs.get(key, "")
    if src == "":
        htmlString = htmlString.replace(r"%%"+key.upper()+r"_HIDDEN%%", "hidden")
    else:
        htmlString = htmlString.replace(r"%%"+key.upper()+r"_HIDDEN%%", "")
    htmlString = htmlString.replace(r"%%"+key.upper()+r"_SRC%%", src)
    return htmlString