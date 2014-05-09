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

def abort_if_duplicate(uuid):
  if len(gdb.nodes.filter(Q('uuid',iexact=uuid))) > 0:
    abort(404, message="Node '{}' already exists".format(uuid))

def abort_if_missing_fields(form, fields):
  for field in fields:
    if field not in form:
      abort(404, message="Missing '{}' field".format(field))


###############
# API Classes #
###############

class Author(Resource):
  def get(self, author_id):
    author_node = gdb.nodes.filter(Q('uuid', iexact=author_id))
    if len(author_node) == 0:
      abort(404, message="Missing author '{}'".format(author_id))
    return author_node[0].properties

  def put(self, author_id):
    abort_if_duplicate(author_id)
    abort_if_missing_fields(request.form, ['name'])

    author_node = gdb.nodes.create(type='author')
    author_node['uuid'] = author_id
    author_node['name'] = request.form['name']


class AuthorList(Resource):
  def get(self):
    author_nodes = gdb.nodes.filter(Q('type', iexact='author'))
    return map(lambda author_node: author_node.properties, author_nodes)


class Document(Resource):
  def put(self, document_id):
    abort_if_duplicate(document_id)
    abort_if_missing_fields(request.form, ['title', 'url'])

    doc_node = gdb.nodes.create(type='document')
    doc_node['uuid'] = document_id
    doc_node['title'] = request.form['title']
    doc_node['url'] = request.form['url']


class DocumentList(Resource):
  def get(self):
    doc_nodes = gdb.nodes.filter(Q('type', iexact='document'))
    return map(lambda doc_node: doc_node.properties, doc_nodes)


class Relationship(Resource):
  # TODO: figure out how to filter by built-in type
  def get(self):
    return map(lambda rel: {'start': rel.start['uuid'], 'end': rel.end['uuid']},
      gdb.relationships.all())


########
# Main #
########
api.add_resource(Author, '/authors/<string:author_id>')
api.add_resource(AuthorList, '/authors')
api.add_resource(Document, '/documents/<string:document_id>')
api.add_resource(DocumentList, '/documents')
api.add_resource(Relationship, '/relationships')
# api.add_resource(RelationshipList, '/relationships')

if __name__ == '__main__':
    app.run(debug=True)