import ndjson
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpmax, fpgrowth

filename = "universities_latest_all.ndjson"
property_list = []

#Open and read the file to a value
with open(filename, encoding="utf-8") as f:
    data = ndjson.load(f)

df = pd.DataFrame(data)

#Walks .ndjson file and extracts the properties
for i in range(len(df)):
    property_list.append(list(df["claims"][i].keys()))

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