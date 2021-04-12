import pandas as pd
import sys
from SPARQLWrapper import SPARQLWrapper, JSON
from pathlib import Path

endpoint_url = "https://query.wikidata.org/sparql"

query = """SELECT ?property ?propertyLabel WHERE {
  ?property wikibase:propertyType ?propertyType .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
ORDER BY ASC(xsd:integer(STRAFTER(STR(?property), 'P')))"""


def get_results(endpoint_url, query):
    user_agent = f"WDQS-example Python/{sys.version_info[0]}.{sys.version_info[1]}"
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

p_df = pd.DataFrame(columns=['Property', 'Value'])

results = get_results(endpoint_url, query)
for result in results["results"]["bindings"]:
    p_df = p_df.append({'Property': (result['property']['value'].split("/")[-1]), 'Value' : result['propertyLabel']['value']}, ignore_index=True)
p_df = p_df.set_index('Property')

p_df.to_csv(Path('../Data/properties.csv'))