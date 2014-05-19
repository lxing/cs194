from flask import Flask, request
from flask.ext.restful import reqparse, abort, Api, Resource

from neo4jrestclient.client import GraphDatabase
from neo4jrestclient.query import Q


app = Flask(__name__)
api = Api(app)
gdb = GraphDatabase('http://localhost:7474/db/data/')

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


###############
# API Classes #
###############
class Author(Resource):
  def get(self, author_id):
    get_by_type_and_uuid('author', author_id).properties

  def put(self, author_id):
    abort_if_duplicate('author', author_id)
    abort_if_missing_fields(request.form, ['name'])

    author_node = gdb.nodes.create(type='author')
    author_node['uuid'] = author_id
    author_node['name'] = request.form['name']

class AuthorList(Resource):
  def get(self):
    author_nodes = gdb.nodes.filter(Q('type', iexact='author'))
    return map(lambda author_node: author_node.properties, author_nodes)

class Document(Resource):
  def get(self, document_id):
    get_by_type_and_uuid('document', document_id).properties

  def put(self, document_id):
    abort_if_duplicate('document', document_id)
    abort_if_missing_fields(request.form, ['title', 'url']) # Add body

    doc_node = gdb.nodes.create(type='document')
    doc_node['uuid'] = document_id
    doc_node['title'] = request.form['title']
    doc_node['url'] = request.form['url']
    doc_node['body'] = request.form['title'] # Change to body later

class DocumentList(Resource):
  def get(self):
    doc_nodes = gdb.nodes.filter(Q('type', iexact='document'))
    return map(lambda doc_node: doc_node.properties, doc_nodes)

class Entity(Resource):
  def get(self, entity_id):
    get_by_type_and_uuid('entity', entity_id).properties

  def put(self, entity_id):
    abort_if_duplicate('entity', entity_id)
    abort_if_missing_fields(request.form, ['name'])

    entity_node = gdb.nodes.create(type='entity')
    entity_node['uuid'] = entity_id
    entity_node['name'] = request.form['name']

class EntityList(Resource):
  def get(self):
    entity_nodes = gdb.nodes.filter(Q('type', iexact='entity'))
    return map(lambda entity_node: entity_node.properties, entity_nodes)


class AuthoredBy(Resource):
  def put(self, document_id, author_id):
    doc_node = get_by_type_and_uuid('document', document_id)
    author_node = get_by_type_and_uuid('author', author_id)
    doc_node.relationships.create('AuthoredBy', author_node, type='AuthoredBy')

class HasEntity(Resource):
  def put(self, document_id, entity_id):
    doc_node = get_by_type_and_uuid('document', document_id)
    entity_node = get_by_type_and_uuid('entity', entity_id)
    doc_node.relationships.create('HasEntity', entity_node, type='HasEntity')

class RelationshipList(Resource):
  def serialize_relationship_entry(self, rel):
    endpoints = {'start': rel.start['uuid'], 'end': rel.end['uuid']}
    return dict(rel.properties.items() + endpoints.items())

  # TODO: figure out how to filter by built-in type
  def get(self, rel_type):
    rels = gdb.relationships.filter(Q('type',iexact=rel_type))
    return map(lambda rel: self.serialize_relationship_entry(rel), rels)


########
# Main #
########
api.add_resource(Author, '/authors/<string:author_id>')
api.add_resource(AuthorList, '/authors')
api.add_resource(Document, '/documents/<string:document_id>')
api.add_resource(DocumentList, '/documents')
api.add_resource(Entity, '/entities/<string:entity_id>')
api.add_resource(EntityList, '/entities')

api.add_resource(AuthoredBy, '/documents/<string:document_id>/authors/<string:author_id>')
api.add_resource(RelationshipList, '/relationships/<string:rel_type>')

if __name__ == '__main__':
    app.run(debug=True)