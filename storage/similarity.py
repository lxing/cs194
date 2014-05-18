from neo4jrestclient.client import GraphDatabase
from neo4jrestclient.query import Q

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

gdb = GraphDatabase('http://localhost:7474/db/data/')

if __name__ == '__main__':
  text_data = []

  doc_nodes = gdb.nodes.filter(Q('type',iexact='document'))
  for i in range(len(doc_nodes)):
    text_data = text_data + [doc_nodes[i]['title']]

  tfidf = TfidfVectorizer().fit_transform(text_data)
  cos_sims = linear_kernel(tfidf, tfidf)

  for i in range(len(doc_nodes)):
    for j in range(len(doc_nodes)):
      doc_nodes[i].relationships.create('SimilarTo',
        doc_nodes[j], weight=cos_sims[i][j], type='SimilarTo')