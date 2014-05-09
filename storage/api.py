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
    abort(404, message="Node {} already exists".format(uuid))

def abort_if_missing_fields(form, fields):
  for field in fields:
    if field not in form:
      abort(404, message="Missing '{}'' field".format(field))


###############
# API Classes #
###############

class Author(Resource):
  def get(self, author_id):
    return author_id

  def put(self, author_id):
    abort_if_duplicate(author_id)
    abort_if_missing_fields(request.form, ['name'])

    author_node = gdb.nodes.create(type='author')
    author_node['name'] = request.form['name']



class Document(Resource):
  def put(self, document_id):
    abort_if_duplicate(document_id)
    abort_if_missing_fields(request.form, ['title', 'url'])

    doc_node = gdb.nodes.create(type='document')
    doc_node['title'] = request.form['title']
    doc_node['url'] = request.form['url']



########
# Main #
########
api.add_resource(Author, '/author/<string:author_id>')
api.add_resource(Document, '/document/<string:document_id>')

if __name__ == '__main__':
    app.run(debug=True)