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
        for properties in lists:
            property_count[properties] = property_count.get(properties, 0) + 1

    # Converts the dictionary to a dataframe
    property_dataframe = pd.DataFrame(list(property_count.items()), columns=['Property', 'Frequency'])
    property_dataframe = property_dataframe.set_index("Property")
    property_dataframe = property_dataframe.sort_values(by=['Frequency'], ascending=False)

    return property_dataframe

def entity_property_count_function(listOfProperties):
    entity_property_count = {}
    for lists in listOfProperties:
        if len(lists) not in entity_property_count:
            entity_property_count.setdefault(len(lists), 0)
            entity_property_count.setdefault(0, len(lists))
        if len(lists) in entity_property_count:
            entity_property_count[len(lists)] += 1

    entity_property_dataframe = pd.DataFrame(list(entity_property_count.items()), columns=['Number of Properties',
                                                                                           '#Universities'])
    entity_property_dataframe = entity_property_dataframe.sort_values(by=['#Universities'], ascending=False)
    column_titles = ['#Universities', "Number of Properties"]
    entity_property_dataframe = entity_property_dataframe.reindex(columns=column_titles)

    return entity_property_dataframe

prop_list = extractProperties(Path("../../Data/universities_latest_all.ndjson"))
df2 = entity_property_count_function(prop_list)
print(df2)

if __name__ == '__main__':

    property_list = extractProperties(Path("../../Data/universities_latest_all.ndjson"))

    df = property_count_function(property_list)
    df = df.drop("P31")

    number_of_properties_above_1000 = []
    number_of_properties_below_1000 = []
    for index, row in df.iterrows():
        if row['Frequency'] > 1000:
            number_of_properties_above_1000.append(index)
        else:
            number_of_properties_below_1000.append(index)

    #print(len(number_of_properties_above_1000))
    #print(len(number_of_properties_below_1000))

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df['Frequency']))
    fig.update_layout(
        xaxis_title="Property",
        yaxis_title="Property Frequency"
    )
    #fig.show()

    #print("The median value for the property frequency is {}".format(df['Frequency'].median()))
    #print("The average value for the property frequency is {}".format(df['Frequency'].mean()))
