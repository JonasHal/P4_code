import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
from pathlib import Path
from Finished_Code.extractPropertiesFromNDJSON import extractProperties, replacePcodesWithPlabels
import fileinput

# with open(Path('../Data/result1-1.txt'), 'r') as file :
#   filedata = file.read()
#
# # Replace the target string
# filedata = filedata.replace(',(', ';(')
# filedata = filedata.replace('properties', 'itemsets')
#
# # Write the file out again
# with open(Path('../Data/result1-1.txt'), 'w') as file:
#   file.write(filedata)

frequent_itemsets_apriori = pd.read_csv(Path('../../Data/result1-1.txt'), sep=';')
frequent_itemsets_apriori.itemsets = [frequent_itemsets_apriori.itemsets[i].replace(' ', '').strip(')(').split(',') for i in range(len(frequent_itemsets_apriori))]
frequent_itemsets_apriori.itemsets = replacePcodesWithPlabels(frequent_itemsets_apriori.itemsets)
frequent_itemsets_apriori.itemsets = [frozenset(frequent_itemsets_apriori.itemsets[i]) for i in range(len(frequent_itemsets_apriori))]
association_rules_apriori = association_rules(frequent_itemsets_apriori, metric="confidence", min_threshold=0.99)

association_rules_apriori["consequents_len"] = association_rules_apriori["consequents"].apply(lambda x: len(x))
association_rules_apriori = association_rules_apriori[
    (association_rules_apriori["consequents_len"] == 1) &
    (association_rules_apriori["leverage"] > 0.0) &
    (association_rules_apriori["lift"] > 1.0)]

association_rules_apriori = association_rules_apriori[['antecedents', 'consequents', 'support', 'confidence', 'lift', 'leverage']]

print(association_rules_apriori.head(10))