# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
import pandas as pd
from pandas import json_normalize
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """SELECT ?item ?itemLabel 
WHERE 
{
  ?item wdt:P31 wd:Q3918.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}"""


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    result = sparql.query().convert()
    return json_normalize(result["results"]["bindings"])

results = get_results(endpoint_url, query)

print(results.columns)
print(results[['item.value', 'itemLabel.value']])
