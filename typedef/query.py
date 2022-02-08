import re

class MyQuery:
    TOP_REGEX = r"TOP:\d+"
    SORT_REGEX = r"\sSORT_BY:\S*"
    FIELD_SEPARATOR = ":"
    DEFAULT_LIMIT = 10
    MAX_LIMIT = 200

    def __init__(self, rQuery):
        self.query = rQuery.strip()
        self.replaceShortcut()
        self.getUserLimit()
        self.getUserSort()
 
    def getUserLimit(self):
        limit = MyQuery.DEFAULT_LIMIT
        matchTop = re.search(MyQuery.TOP_REGEX, str(self.query))
        if matchTop != None:
            numtop = int(matchTop.group().split(MyQuery.FIELD_SEPARATOR)[1])
            limit = numtop
            self.query = self.query.replace(matchTop.group(), "")
        self.limit = min(limit, MyQuery.MAX_LIMIT)

    def getUserSort(self):
        sortedBy = None
        matchSortedBy = re.search(MyQuery.SORT_REGEX, str(self.query))
        if(matchSortedBy != None):
            sortedBy = matchSortedBy.group().split(MyQuery.FIELD_SEPARATOR)[1].strip()
            self.query = self.query.replace(matchSortedBy.group(), "")
        self.sortedBy = sortedBy

    def replaceShortcut(self):
        self.query = self.query.replace("raud", "audienceScore")
        self.query = self.query.replace("rcrt", "tomatometerScore")
        self.query = self.query.replace("imdb", "score")
        match = re.search(r"(\s|\b)ryear", self.query)
        if match != None:
            self.query = self.query.replace("ryear", "releaseYear")

    def getImdbQuery(self):
        q = self.query
        if ('score' in q) or ('audienceScore' not in q and 'tomatometerScore' not in q):
            tmp = self.query
            tmp = MyQuery.removeNumberField(tmp, "audienceScore")
            tmp = MyQuery.removeNumberField(tmp, "tomatometerScore")
            return tmp.strip()
        return ""
        

    def getRottenQuery(self):
        q = self.query
        if ('audienceScore'  in q or 'tomatometerScore'  in q) or ('score' not in q):
            tmp = self.query
            tmp = MyQuery.removeNumberField(tmp, "score")
            return tmp.strip()
        return ""
    
    def getWikiQuery(self):
        q = self.query
        if 'audienceScore'  in q or 'tomatometerScore'  in q or 'score' in q:
            return ""
        tmp = self.query
        tmp = MyQuery.removeNumberField(tmp, "audienceScore")
        tmp = MyQuery.removeNumberField(tmp, "tomatometerScore")
        tmp = MyQuery.removeNumberField(tmp, "score")
        return tmp.strip()

    def removeNumberField(queryS, fieldName):
        regex = r"(\s|\b)" + fr"{fieldName}" + r":(((>|<)?=?)|\[)\S*\]?"
        match = re.search(regex, queryS)
        if match != None:
            queryS = queryS.replace(match.group(), "")
        return queryS

    def getSortedByImdb(self):
        if self.sortedBy == None  or self.sortedBy=="audienceScore" or self.sortedBy=="tomatometerScore":
            return None
        return self.sortedBy
    
    def getSortedByRotten(self):
        if self.sortedBy == None  or self.sortedBy=="score":
            return None
        return self.sortedBy

    def getSortedByWiki(self):
        if self.sortedBy == None  or self.sortedBy=="score" or self.sortedBy=="audienceScore" or self.sortedBy=="tomatometerScore":
            return None
        return self.sortedBy

