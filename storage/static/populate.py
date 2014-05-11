import json

from neo4jrestclient.client import GraphDatabase
from neo4jrestclient.query import Q

gdb = GraphDatabase('http://localhost:7474/db/data/')

if __name__ == '__main__':
    graph = json.loads(open("E:\\rhau\Downloads\miserables.json").read())

    authors = []
    i = 0
    for node in graph["nodes"]:
        author_node = gdb.nodes.create(type='author')
        author_node['uuid'] = i*i
        author_node['name'] = node["name"]
        author_node['group'] = node["group"]

        authors.append(author_node)
        print (author_node['uuid'])
        i = i+1

    for edge in graph["links"]:
        source_index = edge["source"]
        source = authors[source_index]
        
        target_index = edge["target"]
        target = authors[target_index]

        weight = edge["value"]
        print (source_index, target_index, weight)
        source.relationships.create("Knows", target, value=weight)

