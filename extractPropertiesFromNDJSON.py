import ndjson
import pandas as pd
from pathlib import Path

def extractProperties(filename):

    """

    :param filename: What file to open: for example Path("Data/universities_latest_all.ndjson")
    :return: returns a Python list with all the properties from the .ndjson file.
    """

    property_list= []

    with open(filename, encoding="utf-8") as f:
        wikidata = ndjson.load(f)

    wikidata_df = pd.DataFrame(wikidata)

    #Walks the .ndjson file and extracts the properties
    for i in range(len(wikidata_df)):
        property_list.append(list(wikidata_df["claims"][i].keys()))

    return property_list

if __name__ == '__main__':
    property_list = extractProperties(Path("Data/universities_latest_all.ndjson"))
    print(property_list)


