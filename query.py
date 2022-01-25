from os import remove
import re
from unittest.mock import DEFAULT

class MyQuery:
    ALL_REGEX = r"\sALL"
    TOP_REGEX = r"TOP:\d+"
    SORT_REGEX = r"\sSORT_BY:\S*"
    FIELD_SEPARATOR = ":"
    DEFAULT_LIMIT = 10

    def __init__(self, rQuery):
        self.query = rQuery.strip()
        self.getUserLimit()
        self.getUserSort()
        self.replaceShortcut()

    def getUserLimit(self):
        limit = MyQuery.DEFAULT_LIMIT
        matchAll = re.search(MyQuery.ALL_REGEX, str(self.query))
        matchTop = re.search(MyQuery.TOP_REGEX, str(self.query))
        if matchAll != None:
            limit = None
            self.query = self.query[:-len(matchAll.group())].strip()
        elif matchTop != None:
            numtop = int(matchTop.group().split(MyQuery.FIELD_SEPARATOR)[1])
            limit = numtop
            self.query = self.query[:-len(matchTop.group())].strip()
        self.limit = limit

    def getUserSort(self):
        sortedBy = None
        matchSortedBy = re.search(MyQuery.SORT_REGEX, str(self.query))
        if(matchSortedBy != None):
            sortedBy = matchSortedBy.group().split(MyQuery.FIELD_SEPARATOR)[1].strip()
            self.query = self.query[:-len(matchSortedBy.group())].strip()
        self.sortedBy = sortedBy

    def replaceShortcut(self):
        self.query = self.query.replace("raud:", "audienceScore:")
        self.query = self.query.replace("rcrt:", "tomatometerScore:")
        self.query = self.query.replace("imdb:", "score:")
        match = re.search(r"(\s|\b)year:", self.query)
        if match != None:
            self.query = self.query.replace("year:", "releaseYear:")

    def getImdbQuery(self):
        tmp = self.query
        tmp = MyQuery.removeNumberField(tmp, "audienceScore")
        tmp = MyQuery.removeNumberField(tmp, "tomatometerScore")
        return tmp.strip()

    def getRottenQuery(self):
        tmp = self.query
        tmp = MyQuery.removeNumberField(tmp, "score")
        return tmp.strip()
    
    def getWikiQuery(self):
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

query = MyQuery("raud:dog imdb:cat year:2020 bunny")
print(query.limit)