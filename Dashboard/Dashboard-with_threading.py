#github to wikidataintegrator: https://github.com/SuLab/WikidataIntegrator

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import requests
from qwikidata.sparql import return_sparql_query_results
import concurrent.futures

app = dash.Dash(__name__)

SEARCHPAGE = ""
SEARCHENTITY = "Q314"

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

def retrieve_properties(item):
    URL = "https://www.wikidata.org/w/api.php?action=wbgetclaims&entity=%s&format=json&props=" % (item)

    with requests.Session() as S:
        try:
            DATA = dict(S.post(url=URL, headers={"user-agent": "magic browser", "Content-Type": "application/json"}).json())["claims"].keys()
            print("Retrieving properties from " + str(item) + " Succeded")
        except Exception:
            return "Item did not have any properties"

    return list(DATA)


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
        R = S.post(url=URL, headers={"user-agent": "magic browser", "Content-Type": "application/json"})
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
            options=[{"label": i, "value": i} for i in ["Q3918", "Q1337", "Q146", "Q88888888", "Q42069"]],
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

        item_list = []

        for result in results["results"]["bindings"]:
            item_list.append(result['item']['value'].split("/")[-1])

        print("The length of the item list is " + str(len(results["results"]["bindings"])))

        nested_list = []
        loading_bar_progress = 0

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_nested_list = {executor.submit(retrieve_properties, item): item for item in item_list}
            for future in concurrent.futures.as_completed(future_nested_list):
                try:
                    nested_list.append(future.result())
                    loading_bar_progress += 1
                except Exception:
                    loading_bar_progress += 1
                    print("Generated an exception")

        print(nested_list)

if __name__ == '__main__':
    app.run_server(debug=True)