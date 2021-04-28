import timeit
from PropertyDistUni import property_count_function, replacePcodesWithPlabels
from mlxtend.frequent_patterns import fpgrowth, association_rules
from extractPropertiesFromNDJSON import extractProperties
from mlxtend.preprocessing import TransactionEncoder
import plotly.graph_objects as go
from pathlib import Path
from aifc import Error
import pandas as pd

if __name__ == '__main__':
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
    """
    Transform the nested list into a boolean dataframe with transactions on rows and items on columns
    :param property_list: The nested list with the wikidata properties
    :return: A boolean dataframe
    """
    te = TransactionEncoder()
    te_ary = te.fit(property_list).transform(property_list)
    property_dataframe = pd.DataFrame(te_ary, columns=te.columns_)
    #property_dataframe = property_dataframe.drop('P31', axis=1)
    return property_dataframe


def getBoxplotValues(df):
    """
    Calculates the quatilies for the dataframe with items and the count of items
    :param df: A dataframe with columns "item" and "count"
    :return: The number of the threshold used to partition data
    """
    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)

    IQR = Q3 - Q1

    Upper_Fence = Q3 + (1.5 * IQR)

    return Upper_Fence


def splitBooleanDF(df_without_labels, type):
    """
    Partition the dataframe into two groups with the threshold on the Upper Fence
    :param df_without_labels: A boolean df with the P-value as columns
    :param type: Either above or below, decides the output
    :return: The dataframe with the properties in the selected type
    """
    if type == 'above':
        above_threshold = property_count_df_without_labels[
            property_count_df_without_labels['Frequency'] > getBoxplotValues(df_without_labels['Frequency'])]
        above_threshold_df = getBooleanDF(property_list).drop(above_threshold['Property'].tolist(), axis='columns')
        return above_threshold_df
    elif type == 'below':
        below_threshold = property_count_df_without_labels[
            property_count_df_without_labels['Frequency'] <= getBoxplotValues(df_without_labels['Frequency'])]
        below_threshold_df = getBooleanDF(property_list).drop(below_threshold['Property'].tolist(), axis='columns')
        return below_threshold_df
    else:
        raise Error("it can only take above or below. Please try again")


if __name__ == '__main__':
    frequent_items = fpgrowth(splitBooleanDF(property_count_df_without_labels, 'below'),
                                                min_support=0.4, use_colnames=True)

    property_rules = association_rules(frequent_items,
                                       metric="lift", min_threshold=1.1)