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
import plotly.express as px


# The full list of properties
property_list = extractProperties(Path("../Data/universities_latest_all.ndjson"))

# Uses the property_count_function to create a dataframe containing properties and their frequency.
property_count_df = property_count_function(property_list)

# Copy of the property_count_df that should be with P-codes and not P label values
property_count_df_without_labels = property_count_df.copy()

# Uses the function replacePcodesWithPlabels on the dataframe to make a new one with P label values
property_count_df_with_labels = replacePcodesWithPlabels(property_count_df)

fig = px.box(property_count_df_without_labels, x=property_count_df_without_labels['Frequency'], points="all")

#fig.show()


te = TransactionEncoder()
te_ary = te.fit(property_list).transform(property_list)
property_dataframe = pd.DataFrame(te_ary, columns=te.columns_)

Q1 = property_count_df_without_labels['Frequency'].quantile(0.25)
Q3 = property_count_df_without_labels['Frequency'].quantile(0.75)

IQR = Q3 - Q1

Upper_Fence = round(Q3 + (1.5 * IQR), 0)
print(Upper_Fence)
Middle_Ground = round(len(property_dataframe)*0.25, 0)
print(Middle_Ground)

above_threshold = property_count_df_without_labels[property_count_df_without_labels['Frequency'] > Middle_Ground]
print('Der er {} antal properties OVER threshold'.format(len(above_threshold)))

# & means and
between_thresholds = property_count_df_without_labels[(property_count_df_without_labels['Frequency'] <= Middle_Ground) &
                                                      (property_count_df_without_labels['Frequency'] > Upper_Fence)]
print('Der er {} antal properties MELLEM thresholds'.format(len(between_thresholds)))

below_threshold = property_count_df_without_labels[property_count_df_without_labels['Frequency'] <= Upper_Fence]
print('Der er {} antal properties UNDER threshold'.format(len(below_threshold)))

above_threshold_df = property_dataframe.drop(below_threshold['Property'].tolist()+between_thresholds['Property'].tolist()
                                             , axis='columns')

between_thresholds_df = property_dataframe.drop(below_threshold['Property'].tolist()+above_threshold['Property'].tolist()
                                                , axis='columns')

below_threshold_df = property_dataframe.drop(above_threshold['Property'].tolist()+between_thresholds['Property'].tolist()
                                             , axis='columns')

print(above_threshold_df)
print(between_thresholds_df)
print(below_threshold_df)
#apriori_frequent_properties = apriori(property_dataframe, min_support=0.2, use_colnames=True)
#property_rules = association_rules(apriori_frequent_properties, metric="lift", min_threshold=1.1)
#print(property_rules)