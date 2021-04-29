#github to wikidataintegrator: https://github.com/SuLab/WikidataIntegrator

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import requests

app = dash.Dash(__name__)

SEARCHPAGE = ""

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}


app.layout = html.Div([
    html.H1(children='Hello Dash'),

    html.Div(children='Dash: A web application framework for Python.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    html.Div([
        dcc.Input(id="input-1", type="text", value=SEARCHPAGE),
        html.Div(id="number-output"),
    ]),

])

@app.callback(
    Output("number-output", "children"),
    Input("input-1", "value"),
)
def update_output(input1):
    S = requests.Session()
    URL = "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=%s&format=json&limit=10&formatversion=2&language=en" % (input1)

    if len(input1) >= 1:
        R = S.post(url=URL, headers={"user-agent" : "magic browser"})
        DATA = R.json()

        return print(DATA)
    else:
        return ""


if __name__ == '__main__':
    app.run_server(debug=True)