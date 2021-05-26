from findPropertyDist import property_count_function
from mlxtend.frequent_patterns import fpgrowth, association_rules
from extractPropertiesFromNDJSON import extractProperties, replacePcodesWithPlabels
from findPropertyDist import replacePcodesWithPlabels_df
from mlxtend.preprocessing import TransactionEncoder
import plotly.graph_objects as go
from pathlib import Path
import pandas as pd
from plotly.subplots import make_subplots
import time

def getBooleanDF(property_list):
    """
    Transform the nested list into a boolean dataframe with transactions on rows and items on columns
    :param property_list: The nested list with the wikidata properties
    :return: A boolean dataframe
    """
    te = TransactionEncoder()
    te_ary = te.fit(property_list).transform(property_list)
    boolean_dataframe = pd.DataFrame(te_ary, columns=te.columns_)
    # property_dataframe = property_dataframe.drop('P31', axis=1)
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

    overlap_range = 1.5 * IQR
    upper_fence = Q3 + overlap_range

    return upper_fence, overlap_range


def splitBooleanDF(property_list, partition):
    '''
    Takes a nested list creates a boolean_df and partition the data
    :param property_list: Input is the nested property list extracted from extractProperties()
    :return: a list of in total 3 dataframes. Index 0 is the "rarest" properties, index 1 is the middle properties and
    index 2 is the most frequent properties
    '''
    # replace P-codes with P-labels
    property_list = replacePcodesWithPlabels(property_list)

    # Uses the two functions property_count_function() and getBooleanDF()
    df = property_count_function(property_list)
    boolean_df = getBooleanDF(property_list)

    # Define the splits - the lower is the boxplot upperfence and the upper is at the number corresponding to 25 % frequency
    lower_split = round(getBoxplotValues(df)[0], 0)  # Skal være count dataframe - svarer til Upper Fence
    upper_split = round(len(boolean_df) * 0.25, 0)  # Skal være boolean dataframe - svarer til support > 0.25
    overlap_range = round(getBoxplotValues(df)[1], 0)  # Skal være count dataframe - svarer til IQR * 1.5

    if partition == "lower":
        # Define lists of properties belonging to the partitions
        between_splits = df[
            (df['Frequency'] <= upper_split) & (df['Frequency'] > lower_split + overlap_range)]  # & means and
        above_upper_split = df[df['Frequency'] > upper_split]

        # Drops the relevant list of properties from the original boolean dataframe thereby creating the partitioned datasets
        split_df = boolean_df.drop(
            between_splits['Property'].tolist() + above_upper_split['Property'].tolist(),
            axis='columns')

    elif partition == "middle":
        # Define lists of properties belonging to the partitions
        below_lower_split = df[df['Frequency'] <= lower_split - overlap_range]
        above_upper_split = df[df['Frequency'] > upper_split]

        # Drops the relevant list of properties from the original boolean dataframe thereby creating the partitioned datasets
        split_df = boolean_df.drop(
            below_lower_split['Property'].tolist() + above_upper_split['Property'].tolist(),
            axis='columns')

    elif partition == "upper":
        # Define lists of properties belonging to the partitions
        below_lower_split_with_overlap = df[df['Frequency'] <= lower_split + overlap_range]
        between_splits = df[(df['Frequency'] <= upper_split) & (df['Frequency'] > lower_split + overlap_range)]

        # Drops the relevant list of properties from the original boolean dataframe thereby creating the partitioned datasets
        split_df = boolean_df.drop(
            below_lower_split_with_overlap['Property'].tolist() + between_splits['Property'].tolist(),
            axis='columns')

    else:
        raise ValueError("The partition could not be made from the function splitBooleanDF(). "
                         "It has to defined as either 'lower', 'middle' or 'upper'")

    return split_df


def removeExternalId(boolean_df):
    """
    Function used to remove properties of type ExternalId from the booleanDF
    :param boolean_df: The boolean_df created to find frequent_itemsets
    :return: The boolean dataframe without properties of type ExternalId any column
    """
    property_label_dataframe = pd.read_csv(Path("../Data/properties.csv"))
    property_label_dataframe_externalIDs = property_label_dataframe[(property_label_dataframe["Type"] == "ExternalId")]
    property_label_dataframe_externalIDs.set_index(['Value'], inplace=True)

    drop_count = 0
    for column in boolean_df.columns:
        if column in property_label_dataframe_externalIDs.index:
            boolean_df.drop(column, axis='columns', inplace=True)
            drop_count += 1

    print('{} number of columns that are ID"s have been dropped'.format(drop_count))
    return boolean_df


if __name__ == '__main__':
    # The full list of properties
    property_list = extractProperties(Path("../Data/universities_latest_all.ndjson"))

    #Fig 3.1.2
    def makeBoxPlot():
        # Uses the property_count_function to create a dataframe containing properties and their frequency.
        property_count_df = property_count_function(property_list)

        # Copy of the property_count_df that should be with P-codes and not P label values
        property_count_df_without_labels = property_count_df.copy()

        # Uses the function replacePcodesWithPlabels on the dataframe to make a new one with P label values
        property_count_df_with_labels = replacePcodesWithPlabels_df(property_count_df)

        fig = go.Figure()
        fig.add_trace(go.Box(y=property_count_df_without_labels['Frequency'], boxpoints='all', marker_size=3,
                             jitter=0.3, name='Boxplot'))

        fig.add_trace(go.Bar(x=[0.2], y=[81], width=0.1, base=0, name='Lower Partition - Rare Properties'))
        fig.add_trace(go.Bar(x=[0.2], y=[2098], width=0.1, base=31, name='Middle Partition - Properties'))
        fig.add_trace(go.Bar(x=[0.2], y=[6386], width=0.1, base=2129, name='Upper Partition - General Properties'))

        fig.update_layout(
            yaxis_title='Property Frequency',
            xaxis_visible=False, xaxis_showticklabels=False
        )

        fig.show()

        fig2 = make_subplots(rows=1, cols=2)
        fig2.add_trace(go.Box(y=property_count_df_with_labels['Frequency'], boxpoints='all',
                              marker=dict(size=3, color='blue'),
                              jitter=0.3, name='No zoom', ), row=1, col=1)
        fig2.add_trace(go.Box(y=property_count_df_with_labels['Frequency'], boxpoints='all',
                              marker=dict(size=3, color='blue'),
                              jitter=0.3, name='Zoomed in'), row=1, col=2)
        fig2.update_yaxes(title_text='Property Frequency',
                          row=1, col=1)

        fig2.show()
    """
    3.3.1
    """
    # makeBoxPlot()

    # upper_properties = splitBooleanDF(property_list, "upper")
    middle_properties = splitBooleanDF(property_list, "middle")
    # lower_properties = splitBooleanDF(property_list, "lower")

    # frequent_items_lower = fpgrowth(lower_properties, min_support=0.0003, use_colnames=True)
    frequent_items_middle = fpgrowth(middle_properties, min_support=0.006, use_colnames=True)

