# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
import scipy
import networkx as nx
import matplotlib.pyplot as plt
from pandas import json_normalize
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """SELECT ?item ?itemLabel ?instance_of ?instance_ofLabel WHERE {
  ?item wdt:P31 wd:Q3918.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  OPTIONAL { ?item wdt:P31 ?instance_of. }
}"""

def get_results(endpoint_url, query):
    user_agent = "WDS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent) #Agent is required from Wiki's side
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    result = sparql.query().convert() #Convert the query to our specified return format - JSON
    return json_normalize(result["results"]["bindings"]) #Pandas function to convert JSON to DF

results = get_results(endpoint_url, query)

G = nx.DiGraph()
G.add_edges_from([[results['itemLabel.value'][i], results['instance_ofLabel.value'][i]] for i in range(20)])
print("Graph is created with {} nodes and {} edges".format(G.number_of_nodes(), G.number_of_edges()))
pos = nx.spring_layout(G)
nx.draw_networkx(G, pos=pos)
nx.draw_networkx_edge_labels(G, pos=pos)
plt.show()

#I følge Matteo these measures (eccentricitiy, radius and diameter) ignore directions of edges

print('The eccentricitiy of the graph is {}'.format(nx.eccentricity(G.to_undirected()) ) )
print('The radius (minimum eccentricitiy) of the graph is {}'.format(nx.radius(G.to_undirected()) ) )
print('The diameter (maximum eccentricitiy) of the graph is {}'.format(nx.diameter(G.to_undirected()) ) )
print('The density of the graph is {}'.format(nx.density(G)) )
print('The average clustering coefficient of the graph is {}'.format(nx.average_clustering(G)))

