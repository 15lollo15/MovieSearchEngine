def iterToComma(iter):
        string = ""
        for x in iter:
            string += x + ", "
        string = string[:-2]
        return string

def iterToLi(iter):
    string = ""
    for x in iter:
        string += "<li>" + x + "</li>"
    string = string[:-2]
    return string