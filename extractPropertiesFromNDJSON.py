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

#With apriori algorithm and stuff
"""
te = TransactionEncoder()
te_ary = te.fit(property_list).transform(property_list)
df = pd.DataFrame(te_ary, columns=te.columns_)

frequent_itemsets = fpgrowth(df, min_support=0.6, use_colnames=True)
#print(frequent_itemsets.sort_values(by=['support','itemsets'], ascending=True))

frequent_itemsets2 = apriori(df, min_support=0.6, use_colnames=True)
print(frequent_itemsets2.sort_values(by=['support','itemsets'], ascending=True))

frequent_itemsets3 = fpmax(df, min_support=0.6, use_colnames=True)
#print(frequent_itemsets3.sort_values(by=['support','itemsets'], ascending=True))
"""