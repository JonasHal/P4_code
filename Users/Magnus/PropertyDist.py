from extractPropertiesFromNDJSON import extractProperties
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

property_list = extractProperties(Path("../../Data/universities_latest_all.ndjson"))

number_of_properties = len(property_list)
print(number_of_properties)

property_count = {}
for lists in property_list:
    for prop in lists:
        property_count[prop] = property_count.get(prop, 0) + 1

print(property_count)

property_dataframe = pd.DataFrame(list(property_count.items()), columns=['Property', 'Frequency'])
property_dataframe = property_dataframe.sort_values(by=['Frequency'], ascending=False)
print(property_dataframe)

fig = go.Figure()
fig.add_trace(go.Bar(x=property_dataframe['Property'], y=property_dataframe['Frequency']))
fig.show()





