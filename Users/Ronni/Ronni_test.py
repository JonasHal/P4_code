import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpmax, fpgrowth

# dataset = [['Milk', 'Onion', 'Nutmeg', 'Kidney Beans', 'Eggs', 'Yogurt'],
#            ['Dill', 'Onion', 'Nutmeg', 'Kidney Beans', 'Eggs', 'Yogurt'],
#            ['Milk', 'Apple', 'Kidney Beans', 'Eggs'],
#            ['Milk', 'Unicorn', 'Corn', 'Kidney Beans', 'Yogurt'],
#            ['Corn', 'Onion', 'Onion', 'Kidney Beans', 'Ice cream', 'Eggs']]
#
# te = TransactionEncoder()
# te_ary = te.fit(dataset).transform(dataset)
# df = pd.DataFrame(te_ary, columns=te.columns_)
#
# frequent_itemsets =fpgrowth(df, min_support=0.6, use_colnames=True)
# print(frequent_itemsets.sort_values(by='itemsets', ascending=True))
# ### alternatively:
# frequent_itemsets2 = apriori(df, min_support=0.6, use_colnames=True)
# frequent_itemsets3 = fpmax(df, min_support=0.6, use_colnames=True)
# print(frequent_itemsets2.sort_values(by='itemsets', ascending=True))
# print(frequent_itemsets3.sort_values(by='itemsets', ascending=True))

import ndjson
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpmax, fpgrowth
from mlxtend.frequent_patterns import association_rules

filename = "..\\..\\Data\\universities_latest_all.ndjson"
property_list = []

# Open and read the file to a value
with open(filename, encoding="utf-8") as f:
    data = ndjson.load(f)

df = pd.DataFrame(data)

# Walks .ndjson file and extracts the properties
for i in range(len(df)):
    property_list.append(list(df["claims"][i].keys()))

te = TransactionEncoder()
te_ary = te.fit(property_list).transform(property_list)
df = pd.DataFrame(te_ary, columns=te.columns_)

# FPgrowth algorithm:

frequent_itemsets_growth = fpgrowth(df, min_support=0.5, use_colnames=True)
# print(frequent_itemsets_growth.info())
# print(frequent_itemsets_growth.describe())

association_rules_growth = association_rules(frequent_itemsets_growth, metric="confidence", min_threshold=0.7)
# print(association_rules.info())
# print(association_rules_growth.head(10))

rules_growth = association_rules(frequent_itemsets_growth, metric="lift", min_threshold=1.2)
rules_growth["antecedent_len"] = rules_growth["antecedents"].apply(lambda x: len(x))
rules_growth = rules_growth[
    (rules_growth["antecedent_len"] >= 2) &
    (rules_growth["confidence"] > 0.75) &
    (rules_growth["lift"] > 1.2)]
rules_growth = rules_growth[['antecedents', 'consequents', 'support', 'confidence', 'lift', 'leverage']]
print(rules_growth.head(25))

# Apriori algorithm:
frequent_itemsets_apriori = apriori(df, min_support=0.5, use_colnames=True)
association_rules_apriori = association_rules(frequent_itemsets_apriori, metric="confidence", min_threshold=0.7)
# print(association_rules_apriori.head(10))

rules_apriori = association_rules(frequent_itemsets_apriori, metric="lift", min_threshold=1.2)
rules_apriori["antecedent_len"] = rules_apriori["antecedents"].apply(lambda x: len(x))
rules_apriori = rules_apriori[
    (rules_apriori["antecedent_len"] >= 2) &
    (rules_apriori["confidence"] > 0.75) &
    (rules_apriori["lift"] > 1.2)]
rules_apriori = rules_apriori[['antecedents', 'consequents', 'support', 'confidence', 'lift', 'leverage']]
# print(rules_apriori.head(25))

# FPmax algorithm:
frequent_itemsets_max = fpmax(df, min_support=0.6, use_colnames=True)
# association_rules_max = association_rules(frequent_itemsets_max, metric="confidence", min_threshold=0.7)
# print(association_rules_max.head(10))

# Sammenligning mellem to hyppige itemsets
# compared = frequent_itemsets_growth.compare(frequent_itemsets_apriori, keep_equal=True)
# print(compared.head(10))
