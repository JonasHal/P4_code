from extractPropertiesFromNDJSON import extractProperties
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go


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
    property_dataframe = property_dataframe.set_index("Property")
    property_dataframe = property_dataframe.sort_values(by=['Frequency'], ascending=False)

    return property_dataframe


def entity_property_count_function(listOfProperties):
    """

    :param listOfProperties: Input is the listOfProperties, use the function extractProperties.
    The for loop expects a nested list.
    :return: returns the entity_property_dataframe containing ['Number of Properties'] and how many universites
    have this exact number in ['#Universities']
    """
    entity_property_count = {}
    for lists in listOfProperties:
        if len(lists) not in entity_property_count:
            entity_property_count.setdefault(len(lists), 1)
        elif len(lists) in entity_property_count:
            entity_property_count[len(lists)] += 1

    entity_property_dataframe = pd.DataFrame(list(entity_property_count.items()), columns=['#Properties',
                                                                                           '#Universities'])
    entity_property_dataframe = entity_property_dataframe.sort_values(by=['#Properties'], ascending=True)
    #The next two lines switches the two columns.
    column_titles = ['#Universities', "#Properties"]
    entity_property_dataframe = entity_property_dataframe.reindex(columns=column_titles)

    return entity_property_dataframe


if __name__ == '__main__':

    property_list = extractProperties(Path("../../Data/universities_latest_all.ndjson"))

    df = property_count_function(property_list)
    #df = df.drop("P31")

    number_of_properties_above_1000 = []
    number_of_properties_below_1000 = []
    for index, row in df.iterrows():
        if row['Frequency'] > 1000:
            number_of_properties_above_1000.append(index)
        else:
            number_of_properties_below_1000.append(index)

    # print(len(number_of_properties_above_1000))
    # print(len(number_of_properties_below_1000))

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df['Frequency']))
    fig.update_layout(
        xaxis_title="Property",
        yaxis_title="Property Frequency"
    )
    #fig.show()

    # print("The median value for the property frequency is {}".format(df['Frequency'].median()))
    # print("The average value for the property frequency is {}".format(df['Frequency'].mean()))

    df2 = entity_property_count_function(property_list)

    violin_plot = go.Figure(data=go.Violin(y=df2["#Properties"], fillcolor="lightblue", points="all", box_visible=True,
                                    line_color='black', opacity=0.6, x0="Number of Properties"))
    #violin_plot.update_yaxes(range=[0, 140])
    #violin_plot.show()

    university_property_fig = go.Figure()
    university_property_fig.add_trace(go.Bar(x=df2['#Properties'], y=df2['#Universities']))
    university_property_fig.update_layout(
        xaxis_title="Number of Properties",
        yaxis_title="Number of Universities"
    )
    #university_property_fig.show()

    #print(df2['#Universities'].sum())
