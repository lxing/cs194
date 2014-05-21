from neo4jrestclient.client import GraphDatabase
from neo4jrestclient.query import Q

gdb = GraphDatabase('http://localhost:7474/db/data/')
idx = None
if 'idx' in gdb.nodes.indexes.keys():
  idx = gdb.nodes.indexes.get('idx')
else:
  idx = gdb.nodes.indexes.create('idx',type='fulltext',provider='lucene')

def index_doc_node(node):
  idx['documents'][node['title']] = node
  idx['documents'][node['body']] = node

def index_author_node(node):
  idx['authors'][node['name']] = node

def index_entity_node(node):
  idx['entities'][node['name']] = node



if __name__ == '__main__':
  for node in gdb.nodes.all():
    print 'indexing {} {}'.format(node['uuid'], node['type'])
    if node['type'] == 'author':
      index_author_node(node)
    elif node['type'] == 'document':
      index_doc_node(node)
    elif node['type'] == 'entity':
      index_entity_node(node)