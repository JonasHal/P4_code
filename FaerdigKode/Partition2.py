import timeit
from PropertyDistUni import property_count_function, replacePcodesWithPlabels
from mlxtend.frequent_patterns import association_rules, apriori
from extractPropertiesFromNDJSON import extractProperties
from mlxtend.preprocessing import TransactionEncoder
from Algorithms import runAlgorthims
import plotly.graph_objects as go
from pathlib import Path
from aifc import Error
import pandas as pd


# The full list of properties
property_list = extractProperties(Path("../Data/universities_latest_all.ndjson"))

# Uses the property_count_function to create a dataframe containing properties and their frequency.
property_count_df = property_count_function(property_list)

# Copy of the property_count_df that should be with P-codes and not P label values
property_count_df_without_labels = property_count_df.copy()

# Uses the function replacePcodesWithPlabels on the dataframe to make a new one with P label values
property_count_df_with_labels = replacePcodesWithPlabels(property_count_df)


import plotly.express as px

fig = px.box(property_count_df_without_labels, x=property_count_df_without_labels['Frequency'], points="all")

fig.show()


te = TransactionEncoder()
te_ary = te.fit(property_list).transform(property_list)
property_dataframe = pd.DataFrame(te_ary, columns=te.columns_)
#property_dataframe = property_dataframe.drop('P31', axis=1)

Q1 = property_count_df_without_labels['Frequency'].quantile(0.25)
Q3 = property_count_df_without_labels['Frequency'].quantile(0.75)

IQR = Q3 - Q1

Upper_Fence = Q3 + (1.5 * IQR)


above_trashold = property_count_df_without_labels[property_count_df_without_labels['Frequency'] > Upper_Fence]
below_trashold = property_count_df_without_labels[property_count_df_without_labels['Frequency'] <= Upper_Fence]

above_trashold_df = property_dataframe.drop(above_trashold['Property'].tolist(), axis='columns')
below_trashold_df = property_dataframe.drop(below_trashold['Property'].tolist(), axis='columns')

#apriori_frequent_properties = apriori(property_dataframe, min_support=0.2, use_colnames=True)
#property_rules = association_rules(apriori_frequent_properties, metric="lift", min_threshold=1.1)
#print(property_rules)