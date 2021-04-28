from PropertyDistUni import property_count_function, replacePcodesWithPlabels
from mlxtend.frequent_patterns import fpgrowth, association_rules
from extractPropertiesFromNDJSON import extractProperties
from mlxtend.preprocessing import TransactionEncoder
import plotly.graph_objects as go
from pathlib import Path
import pandas as pd

def getBooleanDF(property_list):
    """
    Transform the nested list into a boolean dataframe with transactions on rows and items on columns
    :param property_list: The nested list with the wikidata properties
    :return: A boolean dataframe
    """
    te = TransactionEncoder()
    te_ary = te.fit(property_list).transform(property_list)
    boolean_dataframe = pd.DataFrame(te_ary, columns=te.columns_)
    #property_dataframe = property_dataframe.drop('P31', axis=1)
    return boolean_dataframe


def getBoxplotValues(df):
    """
    Calculates the quatilies for the dataframe with items and the count of items
    :param df: A dataframe with columns "item" and "count"
    :return: The number of the threshold used to partition data
    """
    Q1 = df['Frequency'].quantile(0.25)
    Q3 = df['Frequency'].quantile(0.75)

    IQR = Q3 - Q1

    Upper_Fence = Q3 + (1.5 * IQR)

    return Upper_Fence

def splitBooleanDF(property_list):
    '''

    :param property_list: Input is the nested property list extracted from extractProperties()
    :return: a list of in total 3 dataframes. Index 0 is the "rarest" properties, index 1 is the middle properties and
    index 2 is the most frequent properties
    '''

    #Uses the two functions property_count_function() and getBooleanDF()
    df = property_count_function(property_list)
    boolean_df = getBooleanDF(property_list)

    #Define the splits - the lower is the boxplot upperfence and the upper is at the number corresponding to 25 % frequency
    lower_split = round(getBoxplotValues(df), 0) #Skal være count dataframe - svarer til Upper Fence
    upper_split = round(len(boolean_df)*0.25, 0) #Skal være boolean dataframe - svarer til support > 0.25

    #Define lists of properties belonging to the partitions
    below_lower_split = df[df['Frequency'] <= lower_split]
    between_splits = df[(df['Frequency'] <= upper_split) & (df['Frequency'] > lower_split)] # & means and
    above_upper_split = df[df['Frequency'] > upper_split]

    #Drops the relevant list of properties from the original boolean dataframe thereby creating the partitioned datasets
    below_lower_split_df = boolean_df.drop(between_splits['Property'].tolist() + above_upper_split['Property'].tolist(),
                                           axis='columns')
    between_splits_df = boolean_df.drop(below_lower_split['Property'].tolist() + above_upper_split['Property'].tolist(),
                                        axis='columns')
    above_upper_split_df = boolean_df.drop(below_lower_split['Property'].tolist() + between_splits['Property'].tolist(),
                                           axis='columns')

    return below_lower_split_df, between_splits_df, above_upper_split_df

if __name__ == '__main__':
    # The full list of properties
    property_list = extractProperties(Path("../Data/universities_latest_all.ndjson"))

    def makeBoxPlot():
        # Uses the property_count_function to create a dataframe containing properties and their frequency.
        property_count_df = property_count_function(property_list)

        # Copy of the property_count_df that should be with P-codes and not P label values
        property_count_df_without_labels = property_count_df.copy()

        # Uses the function replacePcodesWithPlabels on the dataframe to make a new one with P label values
        property_count_df_with_labels = replacePcodesWithPlabels(property_count_df)

        fig = go.Figure()
        fig.add_trace(go.Box(x=property_count_df_without_labels['Frequency']))
        fig.show()

    #makeBoxPlot()

    test_df = splitBooleanDF(property_list)[2]

    frequent_items = fpgrowth(test_df, min_support=0.25, use_colnames=True)
