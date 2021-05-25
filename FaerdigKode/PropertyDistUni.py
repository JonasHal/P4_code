from FaerdigKode.extractPropertiesFromNDJSON import extractProperties
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def property_count_function(listOfProperties):
    """

    :param listOfProperties: Input is the listOfProperties, use the function extractProperties.
    The for loop expects a nested list.
    :return: property_dataframe: a dataframe containing the properties extracted from the list and the
    frequency of which they appear
    """

    property_count = {}  # Empty dict, is gonna look like this: property_count{property : count}
    for lists in listOfProperties:
        try:
            for properties in lists:
                property_count[properties] = property_count.get(properties, 0) + 1
        except TypeError as e:
            print(e)

    # Converts the dictionary to a dataframe
    property_dataframe = pd.DataFrame(list(property_count.items()), columns=['Property', 'Frequency'])
    # property_dataframe = property_dataframe.set_index("Property")
    property_dataframe = property_dataframe.sort_values(by=['Frequency'], ascending=False)

    return property_dataframe


def entity_property_count_function(listOfProperties):
    """
    Notice that this function returns both a dataframe and a list.
    When assigning a variable to the return values [0] is the dataframe and [1] is the list.
    i.e. df = entity_property_count_function(listofProperties)[0] and
    list = entity_property_count_function(listofProperties)[1]

    :param listOfProperties: Input is the listOfProperties, use the function extractProperties.
    The for loop expects a nested list.
    :return: returns 1. the entity_property_dataframe containing ['Number of Properties'] and how many universites
    have this exact number in ['#Universities'].
    also returns 2. the number_of_properties_list which is a sorted list of amount of properties in each university item
    """
    entity_property_count = {}
    number_of_properties_list = []
    for lists in listOfProperties:
        if len(lists) not in entity_property_count:
            entity_property_count.setdefault(len(lists), 1)
            number_of_properties_list.append(len(lists))
        elif len(lists) in entity_property_count:
            entity_property_count[len(lists)] += 1
            number_of_properties_list.append(len(lists))

    entity_property_dataframe = pd.DataFrame(list(entity_property_count.items()), columns=['#Properties',
                                                                                           '#Universities'])
    entity_property_dataframe = entity_property_dataframe.sort_values(by=['#Properties'], ascending=True)
    # The next two lines switches the two columns.
    column_titles = ['#Universities', "#Properties"]
    entity_property_dataframe = entity_property_dataframe.reindex(columns=column_titles)

    # Sorts the number_of_properties_list before returning it
    number_of_properties_list = sorted(number_of_properties_list)

    return entity_property_dataframe, number_of_properties_list


def replacePcodesWithPlabels_df(property_dataframe):
    """
    A function that replaces a dataframe column ['Property'] with the property labels from the csv
    propertes.csv.

    :param property_dataframe: Input is a dataframe with the P-codes you want to replace with P-labels.
    Notice(!) in the code that the it expects the P-code column to be called 'Property'!
    :return: property_dataframe: returns a dataframe with the P-codes replaced with P-labels
    """

    # Converts the csv file containing P-codes and P label values to a dataframe
    property_label_dataframe = pd.read_csv(Path("../Data/properties.csv"))

    for prop in property_dataframe['Property']:
        # This for loop goes trough each property and replaces it with each corresponding label
        if prop in list(property_label_dataframe['Property']):
            prop_label_value = property_label_dataframe.loc[property_label_dataframe['Property'] == prop,
                                                            'Value'].iloc[0]

            # This line replaces the P-code with the P label value - Notice inplace=True
            property_dataframe['Property'].replace({prop: prop_label_value}, inplace=True)

    return property_dataframe


if __name__ == '__main__':
    # The full list of properties
    property_list = extractProperties(Path("../Data/universities_latest_all.ndjson"))
    # Uses the property_count_function to create a dataframe containing properties and their frequency.
    property_count_df = property_count_function(property_list)
    # Copy of the property_count_df that should be with P-codes and not P label values
    property_count_df_without_labels = property_count_df.copy()
    # Uses the function replacePcodesWithPlabels on the dataframe to make a new one with P label values
    property_count_df_with_labels = replacePcodesWithPlabels_df(property_count_df)

    number_of_properties_above_1000 = [index for index, row in property_count_df.iterrows() if row['Frequency'] > 1000]
    number_of_properties_below_1000 = [index for index, row in property_count_df.iterrows() if row['Frequency'] <= 1000]

    # Below are the figures
    # Barplot with ALL P-codes and their frequency
    fig_without_labels = go.Figure()
    fig_without_labels.add_trace(go.Bar(x=property_count_df_without_labels['Property'],
                                        y=property_count_df_without_labels['Frequency']))
    fig_without_labels.update_layout(
        xaxis_title="Property", yaxis_title="Property Frequency"
    )
    fig_without_labels.update_yaxes(type='log')
    #fig_without_labels.show()

    # Horizontal barplot with top 24 P label values and their frequency
    fig_with_labels = go.Figure()
    fig_with_labels.add_trace(go.Bar(x=property_count_df_with_labels['Frequency'][0:25],
                                     y=property_count_df_with_labels['Property'],
                                     orientation='h'))
    fig_with_labels.update_layout(
        xaxis_title="Property Frequency",
        yaxis_title="Property"
    )
    #fig_with_labels.show()

    # The two lines below are the dataframe and a list. The list is used for median and average calculations.
    university_property_dataframe = entity_property_count_function(property_list)[0]
    count_list = entity_property_count_function(property_list)[1]

    # Barplot showing how many properties have the exact number of properties in them.
    university_property_fig = go.Figure()
    university_property_fig.add_trace(go.Bar(x=university_property_dataframe['#Properties'],
                                             y=university_property_dataframe['#Universities']))
    university_property_fig.update_layout(
        xaxis_title="Number of Properties",
        yaxis_title="Number of Universities"
    )
    #university_property_fig.show()

    print("The median value for the property frequency is {}".format(np.median(property_count_df['Frequency'])))
    print("The mean value for the property frequency is {}".format(np.average(property_count_df['Frequency'])))
    print("The median value for the amount of properties in universities is {}".format(np.median(count_list)))
    print("The average value for the amount of properties in universities is {}".format(np.average(count_list)))