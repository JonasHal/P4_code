from PropertyDistUni import property_count_function
from mlxtend.frequent_patterns import fpgrowth, association_rules
from extractPropertiesFromNDJSON import extractProperties, replacePcodesWithPlabels
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

    :param property_list: Input is the nested property list extracted from extractProperties()
    :return: a list of in total 3 dataframes. Index 0 is the "rarest" properties, index 1 is the middle properties and
    index 2 is the most frequent properties
    '''
    #replace P-codes with P-labels
    property_list = replacePcodesWithPlabels(property_list)

    # Uses the two functions property_count_function() and getBooleanDF()
    df = property_count_function(property_list)
    boolean_df = getBooleanDF(property_list)


    # Define the splits - the lower is the boxplot upperfence and the upper is at the number corresponding to 25 % frequency
    lower_split = round(getBoxplotValues(df)[0], 0)  # Skal være count dataframe - svarer til Upper Fence
    upper_split = round(len(boolean_df) * 0.25, 0)  # Skal være boolean dataframe - svarer til support > 0.25
    overlap_range = round(getBoxplotValues(df)[1], 0)

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
        fig.add_trace(go.Box(y=property_count_df_without_labels['Frequency'], boxpoints='all', marker_size=3,
                             jitter=0.3, name='Boxplot'))

        fig.add_trace(go.Bar(x=[0.8], y=[81], base=0, name='Partition 1 - Rare Properties'))
        fig.add_trace(go.Bar(x=[0.8], y=[2098], base=31, name='Partition 2 - Properties'))
        fig.add_trace(go.Bar(x=[0.8], y=[6386], base=2129, name='Partition 3 - Frequent Properties'))

        fig.update_layout(
            yaxis_title='Property Frequency',
            xaxis_visible=False, xaxis_showticklabels=False
        )

        fig.show()

        fig2 = go.Figure()
        fig2.add_trace(go.Box(y=property_count_df_with_labels['Frequency']))
        # fig2.show()


    makeBoxPlot()
    
    #upper_properties = splitBooleanDF(property_list, "upper")
    middle_properties = splitBooleanDF(property_list, "middle")
    #lower_properties = splitBooleanDF(property_list, "lower")

    #frequent_items_upper = fpgrowth(upper_properties, min_support=0.25, use_colnames=True)
    frequent_items_middle = fpgrowth(middle_properties, min_support=0.01, use_colnames=True)
    #frequent_items_lower = fpgrowth(lower_properties, min_support=0.002, use_colnames=True)

    print(len(frequent_items_middle))

    rules = association_rules(frequent_items_middle, metric="lift", min_threshold=50)
    print(rules[["antecedents", "consequents"]])

    #Med en confidence
