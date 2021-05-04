from PropertyDistUni import property_count_function
from mlxtend.frequent_patterns import fpgrowth, association_rules
from extractPropertiesFromNDJSON import extractProperties, replacePcodesWithPlabels
from PropertyDistUni import replacePcodesWithPlabels_df
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


def splitBooleanDF(property_list, partition, external_ids = True):
    '''

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
    overlap_range = round(getBoxplotValues(df)[1], 0) # Skal være count dataframe - svarer til IQR * 1.5

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

def removeRulesWithId(rule_df):
    property_label_dataframe = pd.read_csv(Path("../Data/properties.csv"))
    property_label_dataframe_externalIDs = property_label_dataframe[(property_label_dataframe["Type"] == "ExternalId")]
    property_label_dataframe_externalIDs.set_index(['Value'], inplace=True)
    list_of_ids = property_label_dataframe_externalIDs.index.tolist()

    #Changes the datatype of the consequents from frozenset, which is immutable, to a list.
    rule_df['consequents'] = [list(rule_df['consequents'][i]) for i in rule_df.index]

    amount_of_dropped_rules = 0

    for i in rule_df.index:
        if rule_df['consequents'][i][0] in list_of_ids:
            rule_df = rule_df.drop([i])
            amount_of_dropped_rules += 1

    print('A total amount of {} rules have been dropped'.format(amount_of_dropped_rules))

    return rule_df

if __name__ == '__main__':
    # The full list of properties
    property_list = extractProperties(Path("../Data/universities_latest_all.ndjson"))

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

        fig2 = go.Figure()
        fig2.add_trace(go.Box(y=property_count_df_with_labels['Frequency'], boxpoints='all', marker_size=3,
                       jitter=0.3, name='Boxplot'))
        fig2.update_layout(xaxis_title='Property Frequency', xaxis_visible=False, xaxis_showticklabels=False)
        #fig2.show()


    makeBoxPlot()
    
    #upper_properties = splitBooleanDF(property_list, "upper")
    middle_properties = splitBooleanDF(property_list, "middle")
    lower_properties = splitBooleanDF(property_list, "lower")

    #frequent_items_upper = fpgrowth(upper_properties, min_support=0.25, use_colnames=True)
    # frequent_items_middle = fpgrowth(middle_properties, min_support=0.006, use_colnames=True)
    # frequent_items_lower = fpgrowth(lower_properties, min_support=0.0003, use_colnames=True)
    #
    # lower_rules = association_rules(frequent_items_lower, metric="confidence", min_threshold=0.99)
    # lower_rules["consequent_len"] = lower_rules["consequents"].apply(lambda x: len(x))
    # lower_rules = lower_rules[(lower_rules['consequent_len'] == 1) & (lower_rules['lift'] > 1) &
    #                           (lower_rules['leverage'] > 0)]
    #
    # middle_rules = association_rules(frequent_items_middle, metric="confidence", min_threshold=0.99)
    # middle_rules["consequent_len"] = middle_rules["consequents"].apply(lambda x: len(x))
    # middle_rules = middle_rules[(middle_rules['consequent_len'] == 1) & (middle_rules['lift'] > 1) &
    #                             (middle_rules['leverage'] > 0)]
    #
    # middle_rules_without_id = removeRulesWithId(middle_rules)