#github to wikidataintegrator: https://github.com/SuLab/WikidataIntegrator

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import requests

app = dash.Dash(__name__)

SEARCHPAGE = ""
SEARCHENTITY = "Q314"

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}


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
    ])

])

@app.callback(
    Output("search-output", "children"),
    Input("input-1", "value"),
)
def update_output(input1):
    S = requests.Session()
    URL = "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=%s&format=json&limit=5&formatversion=2&language=en" % (input1)

    if len(input1) >= 1:
        R = S.post(url=URL, headers={"user-agent" : "magic browser"})
        DATA = R.json()
        print(DATA)

        return "sd"
    else:
        return ""

#Bruger mediawiki API wbgetclaims til at hente claims fra en item
@app.callback(
    Output("properties-output", "children"),
    Input("input-2", "value"),
)
def extract_properties(input2):
    S = requests.Session()
    URL = "https://www.wikidata.org/w/api.php?action=wbgetclaims&entity=%s&format=json" % (input2)

    R = S.post(url=URL, headers={"user-agent": "magic browser"})
    DATA = R.json()
    DATA_df = pd.DataFrame(DATA)

    property_list = list(DATA_df.index[1:])

    return property_list

if __name__ == '__main__':
    app.run_server(debug=True)