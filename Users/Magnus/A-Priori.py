import pandas as pd
from extractPropertiesFromNDJSON import extractProperties
from pathlib import Path
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth
from mlxtend.frequent_patterns import association_rules

property_list = extractProperties(Path("../../Data/universities_latest_all.ndjson"))

te = TransactionEncoder()
te_ary = te.fit(property_list).transform(property_list)
property_dataframe = pd.DataFrame(te_ary, columns=te.columns_)
property_dataframe = property_dataframe.drop('P31', axis=1)

frequent_properties = fpgrowth(property_dataframe, min_support=0.6, use_colnames=True)

property_rules = association_rules(frequent_properties, metric="confidence", min_threshold=0.7)
print(property_rules)
