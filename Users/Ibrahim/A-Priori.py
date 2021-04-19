import numpy
import pandas as pd
from pathlib import Path
from extractPropertiesFromNDJSON import extractProperties
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

property_list = extractProperties(Path("../../Data/universities_latest_all.ndjson"))

#print(property_list)

te = TransactionEncoder()
te_ary = te.fit(property_list).transform(property_list)
property_dataframe = pd.DataFrame(te_ary, columns=te.columns_)
property_dataframe = property_dataframe.drop('P31', axis=1)
#print(property_dataframe)


property_label_dataframe = pd.read_csv(Path("../../Data/properties.csv"))

for prop in property_dataframe.columns:
    # This for loop goes trough each property and replaces it with each corresponding label
    if prop in list(property_label_dataframe['Property']):
        prop_label_value = property_label_dataframe.loc[property_label_dataframe['Property'] == prop,
                                                         'Value'].iloc[0]
        # # This line replaces the P-code with the P label value
        property_dataframe.rename({prop: prop_label_value}, axis='columns', inplace=True)

frequent_properties = apriori(property_dataframe, min_support=0.7, use_colnames=True)
property_rules = association_rules(frequent_properties, metric="lift", min_threshold=1.1)

#print(property_dataframe['country, official website'].sum())

print(property_rules.to_string())