from PropertyDistUni import property_count_function, replacePcodesWithPlabels
from mlxtend.frequent_patterns import association_rules
from extractPropertiesFromNDJSON import extractProperties
from mlxtend.preprocessing import TransactionEncoder
from Algorthims import runAlgorthims
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

fig = go.Figure()
fig.add_trace(go.Box(x=property_count_df_without_labels['Frequency']))
fig.show()

def getBooleanDF(property_list):

    te = TransactionEncoder()
    te_ary = te.fit(property_list).transform(property_list)
    property_dataframe = pd.DataFrame(te_ary, columns=te.columns_)
    #property_dataframe = property_dataframe.drop('P31', axis=1)
    return property_dataframe


def getBoxplotValues(df):
    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)

    IQR = Q3 - Q1

    Upper_Fence = Q3 + (1.5 * IQR)

    return Upper_Fence


def splitBooleanDF(type):
    above_trashold = property_count_df_without_labels[property_count_df_without_labels['Frequency'] > getBoxplotValues(property_count_df_without_labels['Frequency'])]
    below_trashold = property_count_df_without_labels[property_count_df_without_labels['Frequency'] <= getBoxplotValues(property_count_df_without_labels['Frequency'])]

    above_trashold_df = getBooleanDF(property_list).drop(above_trashold['Property'].tolist(), axis='columns')
    below_trashold_df = getBooleanDF(property_list).drop(below_trashold['Property'].tolist(), axis='columns')

    if type == 'above':
        return above_trashold_df
    elif type == 'below':
        return below_trashold_df
    else:
        raise Error("it can only take above or below. Please try again")


if __name__ == '__main__':
    #print(runAlgorthims(splitBooleanDF('below'), 'apriori').to_string())
    property_rules = association_rules(runAlgorthims(splitBooleanDF('below'), 'apriori', 0.2), metric="lift", min_threshold=1.1)
    print(property_rules)