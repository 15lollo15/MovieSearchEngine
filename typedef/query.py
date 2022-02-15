import re

class MyQuery:
    FIELD_SEPARATOR = r":"   
    TOP_REGEX = r"TOP"+FIELD_SEPARATOR+r"\d+"          # TOP query pattern
    SORT_REGEX = r"\sSORT_BY"+FIELD_SEPARATOR+r"\S*"   # SORT BY ATTRIBUTE query pattern     
    DEFAULT_LIMIT = 10                                 # Default number of results
    MAX_LIMIT = 200                                    # Max number of results that the user can request with TOP

    def __init__(self, rQuery):
        self.query = rQuery.strip()
        self.replaceShortcut()
        self.getUserLimit()
        self.getUserSort()
 
    def getUserLimit(self):
        '''Extract the limit specified with TOP if found'''
        limit = MyQuery.DEFAULT_LIMIT
        matchTop = re.search(MyQuery.TOP_REGEX, str(self.query))
        if matchTop != None:
            numtop = int(matchTop.group().split(MyQuery.FIELD_SEPARATOR)[1])
            limit = numtop
            self.query = self.query.replace(matchTop.group(), "")
        self.limit = min(limit, MyQuery.MAX_LIMIT)

    def getUserSort(self):
        '''Extract the sort field specified with SORT_BY if found'''
        sortedBy = None
        matchSortedBy = re.search(MyQuery.SORT_REGEX, str(self.query))
        if(matchSortedBy != None):
            sortedBy = matchSortedBy.group().split(MyQuery.FIELD_SEPARATOR)[1].strip()
            self.query = self.query.replace(matchSortedBy.group(), "")
        self.sortedBy = sortedBy

    def replaceShortcut(self):
        '''Replace the shortcuts with the original name'''
        self.query = self.query.replace("raud", "audienceScore")
        self.query = self.query.replace("rcrt", "tomatometerScore")
        self.query = self.query.replace("imdb", "score")
        match = re.search(r"(\s|\b)ryear", self.query)
        if match != None:
            self.query = self.query.replace("ryear", "releaseYear")

    def getImdbQuery(self):
        '''Return a valid query for IMDB Index'''
        if self.searchableInImdb():
            tmp = self.query
            tmp = MyQuery.removeNumberField(tmp, "audienceScore")
            tmp = MyQuery.removeNumberField(tmp, "tomatometerScore")
            return tmp.strip()
        return ""
        
    def searchableInImdb(self):
        '''Return True if the query respects the IMDB Index Scheme, False otherwise'''
        q = self.query
        return (('score' in q) or ('audienceScore' not in q and 'tomatometerScore' not in q)) and self.sortedBy != 'audienceScore' and self.sortedBy != 'tomatometerScore'
    
    def searchableInRotten(self):
        '''Return True if the query respects the Rotten Index Scheme, False otherwise'''
        q = self.query
        return (('audienceScore'  in q or 'tomatometerScore'  in q) or ('score' not in q)) and self.sortedBy != 'score'
    
    def searchableInWiki(self):
        '''Return True if the query respects the Wiki Index Scheme, False otherwise'''
        q = self.query
        return (not('audienceScore'  in q or 'tomatometerScore'  in q or 'score' in q)) and self.sortedBy != 'audienceScore' and self.sortedBy != 'tomatometerScore' and self.sortedBy != 'score'
    
    def toKill(self):
        '''Return True if not common movies must be removed'''
        return "score" in self.getImdbQuery() and ('audienceScore' in self.getRottenQuery() or 'tomatometerScore' in self.getRottenQuery())

    def getRottenQuery(self):
        '''Return a valid query for Rotten Index'''
        if self.searchableInRotten():
            tmp = self.query
            tmp = MyQuery.removeNumberField(tmp, "score")
            return tmp.strip()
        return ""
    
    def getWikiQuery(self):
        '''Return a valid query for Wikipedia Index'''
        if not self.searchableInWiki():
            return ""
        tmp = self.query
        tmp = MyQuery.removeNumberField(tmp, "audienceScore")
        tmp = MyQuery.removeNumberField(tmp, "tomatometerScore")
        tmp = MyQuery.removeNumberField(tmp, "score")
        return tmp.strip()

    def removeNumberField(queryS, fieldName):
        '''Remove field containing numbers given in put from the query'''
        regex = r"(\s|\b)" + fr"{fieldName}" + r":(((>|<)?=?)|\[)\S*\]?"
        match = re.search(regex, queryS)
        if match != None:
            queryS = queryS.replace(match.group(), "")
        return queryS

    def getSortedByImdb(self):
        '''Return the sort preference to pass to the IMDB Searcher'''
        if self.sortedBy == None  or self.sortedBy=="audienceScore" or self.sortedBy=="tomatometerScore":
            return None
        return self.sortedBy
    
    def getSortedByRotten(self):
        '''Return the sort preference to pass to the Rotten Searcher'''
        if self.sortedBy == None  or self.sortedBy=="score":
            return None
        return self.sortedBy

    def getSortedByWiki(self):
        '''Return the sort preference to pass to the Wiki Searcher'''
        if self.sortedBy == None  or self.sortedBy=="score" or self.sortedBy=="audienceScore" or self.sortedBy=="tomatometerScore":
            return None
        return self.sortedBy

