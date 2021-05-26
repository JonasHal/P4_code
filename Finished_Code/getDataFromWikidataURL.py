# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

query = """SELECT ?entityLabel ?item ?itemLabel ?wd ?wdLabel ?ps_Label ?wdpqLabel ?pq_Label {
  VALUES (?property ?entity) {(wdt:P31 wd:Q15407956)}

  ?item ?property ?entity .
  ?item ?p ?statement .
  ?statement ?ps ?ps_ .

  ?wd wikibase:claim ?p.
  ?wd wikibase:statementProperty ?ps.

  OPTIONAL {
  ?statement ?pq ?pq_ .
  ?wdpq wikibase:qualifier ?pq .
  }

  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
} 

ORDER BY ?entityLabel ?statement ?ps_"""


def get_results(endpoint_url = "https://query.wikidata.org/sparql", query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


results = get_results(endpoint_url, query)

for result in results["results"]["bindings"]:
    print(result)

print(str(len(results["results"]["bindings"])) + " statements found")
