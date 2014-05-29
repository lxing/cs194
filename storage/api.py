from flask import Flask, request
from flask.ext.restful import reqparse, abort, Api, Resource

from neo4jrestclient.client import GraphDatabase
from neo4jrestclient.query import Q

#from index import *

app = Flask(__name__)
api = Api(app)
gdb = GraphDatabase('http://localhost:7474/db/data/')

# The dumbest cache ever. Preload relationships permanently
rel_cache = {}


# idx = None
# if 'idx' in gdb.nodes.indexes.keys():
#   idx = gdb.nodes.indexes.get('idx')
# else:
#   idx = gdb.nodes.indexes.create('idx',type='fulltext',provider='lucene')

#####################
# Utility Functions #
#####################
def get_by_type_and_uuid(type, uuid):
  nodes = gdb.nodes.filter(Q('type',iexact=type) & Q('uuid',iexact=uuid))
  if len(nodes) == 0:
    abort(404, message="Node '{}' doesn't exist".format(uuid))
  return nodes[0]

def abort_if_duplicate(type, uuid):
  if len(gdb.nodes.filter(Q('type',iexact=type) & Q('uuid',iexact=uuid))) > 0:
    abort(403, message="Node '{}' already exists".format(uuid))

def abort_if_missing_fields(form, fields):
  for field in fields:
    if field not in form:
      abort(400, message="Missing '{}' field".format(field))

def serialize_node(node):
  if node['type'] == 'author':
    return node.properties
  elif node['type'] == 'document':
    node_serialized = node.properties
    del node_serialized['body']
    return node_serialized
  elif node['type'] == 'entity':
    return node.properties

def serialize_relationship(self, rel):
    endpoints = {'start': rel.start['uuid'], 'end': rel.end['uuid']}
    return dict(rel.properties.items() + endpoints.items())


###############
# API Classes #
###############
class Author(Resource):
  def get(self, author_id):
    return get_by_type_and_uuid('author', author_id).properties

  def put(self, author_id):
    abort_if_duplicate('author', author_id)
    abort_if_missing_fields(request.form, ['name'])

    author_node = gdb.nodes.create(type='author')
    author_node['uuid'] = author_id
    author_node['name'] = request.form['name']


class AuthorList(Resource):
  def get(self):
    author_nodes = gdb.nodes.filter(Q('type', iexact='author'))
    return map(lambda author_node: serialize_node(author_node), author_nodes)


class Document(Resource):
  def get(self, doc_id):
    return serialize_node(get_by_type_and_uuid('document', doc_id))

  def put(self, doc_id):
    abort_if_duplicate('document', doc_id)
    abort_if_missing_fields(request.form, ['title', 'url', 'body']) # Add body

    doc_node = gdb.nodes.create(type='document')
    doc_node['uuid'] = doc_id
    doc_node['title'] = request.form['title']
    doc_node['url'] = request.form['url']
    doc_node['body'] = request.form['body']


class DocumentList(Resource):
  def get(self):
    doc_nodes = gdb.nodes.filter(Q('type', iexact='document'))
    return map(lambda doc_node: serialize_node(doc_node), doc_nodes)


class Entity(Resource):
  def get(self, entity_id):
    return serialize_node(get_by_type_and_uuid('entity', entity_id))

  def put(self, entity_id):
    abort_if_duplicate('entity', entity_id)
    abort_if_missing_fields(request.form, ['name'])

    entity_node = gdb.nodes.create(type='entity')
    entity_node['uuid'] = entity_id
    entity_node['name'] = request.form['name']


class EntityList(Resource):
  def get(self):
    entity_nodes = gdb.nodes.filter(Q('type', iexact='entity'))
    return map(lambda entity_node: serialize_node(entity_node), entity_nodes)



class AuthoredBy(Resource):
  def put(self, doc_id, author_id):
    doc_node = get_by_type_and_uuid('document', doc_id)
    author_node = get_by_type_and_uuid('author', author_id)
    doc_node.relationships.create('AuthoredBy', author_node, type='AuthoredBy')

class HasEntity(Resource):
  def put(self, doc_id, entity_id):
    doc_node = get_by_type_and_uuid('document', doc_id)
    entity_node = get_by_type_and_uuid('entity', entity_id)
    doc_node.relationships.create('HasEntity', entity_node, type='HasEntity')

class Cites(Resource):
  def put(self, source_id, dest_id):
    source_node = get_by_type_and_uuid('document', source_id)
    dest_node = get_by_type_and_uuid('document', dest_id)
    source_node.relationships.create('Cites', dest_node, type='Cites')


class RelationshipList(Resource):
  # TODO: figure out how to filter by built-in type
  def get(self, rel_type):
    rels = gdb.relationships.filter(Q('type',iexact=rel_type))
    return map(lambda rel: serialize_relationship(rel), rels)


class Search(Resource):
  def get(self):
    abort_if_missing_fields(request.args, ['query'])
    query = request.args['query']
    results = gdb.nodes.filter(
      Q('title',icontains=query)|
      Q('body',icontains=query)|
      Q('name',icontains=query))
    return map(lambda node: serialize_node(node), results)

# For now, only searcharound outgoing rels
# Return both the relationships and the endpoint nodes
class SearchAround(Resource):
  def get(self, doc_id, rel_type):
    doc_node = get_by_type_and_uuid('document', doc_id)
    rels = doc_node.relationships.outgoing(types=[rel_type])

    rels_serialized = map(lambda rel: serialize_relationship(rel), rels)
    nodes_serialized = map(lambda rel: serialize_node(rel.end), rels)
    return {
      relationships: rels_serialized,
      nodes: nodes_serialized
    }





########
# Main #
########
api.add_resource(Author, '/authors/<string:author_id>')
api.add_resource(AuthorList, '/authors')
api.add_resource(Document, '/documents/<string:doc_id>')
api.add_resource(DocumentList, '/documents')
api.add_resource(Entity, '/entities/<string:entity_id>')
api.add_resource(EntityList, '/entities')

api.add_resource(AuthoredBy, '/documents/<string:doc_id>/authors/<string:author_id>')
api.add_resource(HasEntity, '/documents/<string:doc_id>/entities/<string:entity_id>')
api.add_resource(Cites, '/documents/<string:source_id>/cites/<string:dest_id>')
api.add_resource(RelationshipList, '/relationships/<string:rel_type>')

api.add_resource(Search, '/search')
api.add_resource(SearchAround, '/searchAround/<string:node_type>/<string:rel_type>/')

if __name__ == '__main__':
    app.run(debug=True)