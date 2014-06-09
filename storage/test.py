from neo4jrestclient.client import GraphDatabase
from neo4jrestclient.query import Q

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

gdb = GraphDatabase('http://localhost:7474/db/data/')
# vectorizer = TfidfVectorizer()

# idx = None
# if 'idx' in gdb.nodes.indexes.keys():
#   idx = gdb.nodes.indexes.get('idx')
# else:
#   idx = gdb.nodes.indexes.create('idx',type='fulltext',provider='lucene')