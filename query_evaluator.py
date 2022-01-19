import re
from whoosh.qparser import QueryParser
from whoosh.qparser import GtLtPlugin
from whoosh import qparser

def setQueryParser(qp):
    qp.replace_plugin(GtLtPlugin())
    qp.remove_plugin_class(qparser.WildcardPlugin)