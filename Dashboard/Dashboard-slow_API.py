#github to wikidataintegrator: https://github.com/SuLab/WikidataIntegrator

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import requests
from qwikidata.sparql import return_sparql_query_results
from mlxtend.frequent_patterns import fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder

app = dash.Dash(__name__)

SEARCHPAGE = ""
SEARCHENTITY = "Q314"

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

def retrieve_properties(item):
    S = requests.Session()
    URL = "https://www.wikidata.org/w/api.php?action=wbgetclaims&entity=%s&format=json" % (item)

    DATA = dict(S.post(url=URL, headers={"user-agent": "magic browser", "Content-Type": "application/json"}).json())["claims"].keys()
    S.close()

    return list(DATA)

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

#The HTML Layout
app.layout = html.Div([
    html.Header(html.H1(children='Hello Dash')
    ),

    html.Div(children='Dash: A web application framework for Python.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    html.H2(children="Search Bar"),

    html.Div([
        dcc.Input(id="input-1", type="text", value=SEARCHPAGE),
        html.Div(id="search-output"),
    ]),

    html.H2(children="Retrieve Properties"),

    html.Div([
        dcc.Input(id="input-2", type="text", value=SEARCHENTITY, debounce=True),
        html.Div(id="properties-output")
    ]),

    html.H2(children="Input Properties"),

    html.Div([
        html.Button("Add Filter", id="add-filter", n_clicks=0,
                    style={"grid-column": "1 / span 2"}
                    ),
        html.Div(id="properties_dropdown-container", children=[],
                 style={"width": "240px"}
                 ),
        html.Div(id="values_dropdown-container", children=[],
                 style={"width": "240px"}
                 ),
        html.Div(id="dropdown-container-output")
    ], style={"display": "inline-grid",
              "grid-gap": "24px",
              "grid-template-columns": "auto auto"}
    ),

    html.H2(children="Get Suggestions"),

    html.Div([html.Button("Get Suggestions", id="find-suggestions", n_clicks=0),
              html.Div(id="suggestion-output")
             ])

])

#Search bar
@app.callback(
    Output("search-output", "children"),
    Input("input-1", "value"),
)
def update_output(input1):
    S = requests.Session()
    URL = "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=%s&format=json&limit=5&formatversion=2&language=en" % (input1)

    if len(input1) >= 1:
        R = S.post(url=URL, headers={"user-agent" : "magic browser", "Content-Type": "application/json"})
        DATA = R.json()

        return print(DATA)
    else:
        return ""

#Bruger mediawiki API wbgetclaims til at hente claims fra en item
@app.callback(
    Output("properties-output", "children"),
    Input("input-2", "value"),
)
def extract_properties(input2):
    return retrieve_properties(input2)

#Properties and Values Input: https://dash.plotly.com/dash-core-components/dropdown (Dynamic Options)
@app.callback(
    Output("properties_dropdown-container", "children"),
    Input("add-filter", "n_clicks"),
    State('properties_dropdown-container', 'children'),
)
def display_dropdowns_properties(n_clicks, children):
    new_dropdown = dcc.Dropdown(
            id={
                'type': 'property_filter-dropdown',
                'index': n_clicks
            },
            options=[{"label": i, "value": i} for i in ["P31", "P17", "P51", "P69", "P420"]],
            placeholder = "Select a Property...",
            style={"margin-top": "5px"}
        )
    children.append(new_dropdown)
    return children

@app.callback(
    Output("values_dropdown-container", "children"),
    Input("add-filter", "n_clicks"),
    State('values_dropdown-container', 'children'),
)
def display_dropdowns_values(n_clicks, children):
    new_dropdown = dcc.Dropdown(
            id={
                'type': 'values_filter-dropdown',
                'index': n_clicks
            },
            options=[{"label": i, "value": i} for i in ["Q3918", "Q1337", "Q12321234", "Q88888888", "Q42069"]],
            placeholder="No Value",
            style={"margin-top": "5px"}
        )
    children.append(new_dropdown)
    return children

@app.callback(
    Output("suggestion-output", "children"),
    Input("find-suggestions", "n_clicks"),
    State("properties_dropdown-container", "children"),
    State("values_dropdown-container", "children")
)
def find_suggestions(n_clicks, properties, values):
    if n_clicks >= 1:
        #SPARQL Query Creation
        filters = ""
        for i in range(len(properties)):
            try:
                temp_property = properties[i]['props']['value']
                temp_value = values[i]['props']['value']
                filters += "?item wdt:" + temp_property + " wd:" + temp_value + " . "
            except:
                try:
                    temp_property = properties[i]['props']['value']
                    temp_value = "?variable" + str(i + 1)
                    filters += "?item wdt:" + temp_property + temp_value + " . "
                except:
                    pass

        query_string = """ SELECT ?item WHERE {""" +filters+"""}"""

        results = return_sparql_query_results(query_string)

        #Extract Properties from the results
        property_list = []

        count = 0

        print("The length of the item list is " + str(len(results["results"]["bindings"])))
        for result in results["results"]["bindings"]:
            if count < 100:
                try:
                    item = result['item']['value'].split("/")[-1]
                    print(item)
                    property_list.append(retrieve_properties(item))
                    count += 1
                except:
                    return "Please enter properties to filter the data"
            else:
                break

        if len(property_list) > 1:
            # Uses the two functions property_count_function() and getBooleanDF()
            df = property_count_function(property_list)
            boolean_df = getBooleanDF(property_list)

            print("boolean_df Done")
            frequent_items = fpgrowth(boolean_df, min_support=0.7, use_colnames=True)

            print("frequent_items Done")
            print(frequent_items)
            rules = association_rules(frequent_items, metric="confidence", min_threshold=0.8)

            rules["consequent_len"] = rules["consequents"].apply(lambda x: len(x))
            rules = rules[(rules['consequent_len'] == 1) & (rules['lift'] > 1) &
                                       (rules['leverage'] > 0)]

            print(rules)

            print("DONE")
        else:
            return "Only one item could be found with the given inputs"


if __name__ == '__main__':
    app.run_server(debug=True)