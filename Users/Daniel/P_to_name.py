#Hvis man skal bruge flere P'er printet, kan man med fordel køre dette script én gang
#og efterfølgende kalde f.eks. p_dict['P6'] i sin konsol
import sys
from SPARQLWrapper import SPARQLWrapper, JSON

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


results = get_results(endpoint_url, query)
p_dict = dict()
for result in results["results"]["bindings"]:
    p_dict[result['property']['value'].split("/")[-1]] = result['propertyLabel']['value']


# Når jeg bliver til et modul, kan I importere mig som funktion
#TODO: gem p_dict som fil, så den kan indlæses uden at oprette forbindelse til Wikidata
def get_property_name(p):
    if p in p_dict.keys():
        return p_dict[p]
    else:
        return("Property " + p + " not found")


print(get_property_name('P31'))