import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State

app = dash.Dash()

app.layout = html.Div(
    [
        dcc.Interval(id="interval", interval=10000),
        dcc.Checklist(
            id="checklist",
            options=[
                {"label": "value 1", "value": 1},
                {"label": "value 2", "value": 2},
                {"label": "value 3", "value": 3},
            ],
            value=[1],
        ),
        dcc.Dropdown(id="dropdown"),
    ]
)

html.Div(children=[
    html.Div(children=[
      dcc.Dropdown(id='dropdown_students_cols', options=[{'label': i, 'value': i} for i in list(filter(lambda x: x!='userid', list(df)))], value='component'),
    ]),
    html.Div(children=[
      dcc.Dropdown(id='dropdown_row_names'),
    ]),
])

@app.callback(
  Output(component_id='dropdown_row_names', component_property='options'),
  [Input(component_id='dropdown_students_cols', component_property='value')],)
def get_row_names(column_name='component'):
  row_names = df[column_name].unique().tolist()
  lst = [{'label': i, 'value': i} for i in row_names]
  print(lst)
  return lst


@app.callback(
    [Output("dropdown", "options"), Output("dropdown", "value")],
    [Input("interval", "n_intervals")],
    [State("dropdown", "value"), State("checklist", "values")]
)
def make_dropdown_options(n, value, values):
    options = [{"label": f"Option {v}", "value": v} for v in values]

    if value not in [o["value"] for o in options]:
        # if the value is not in the new options list, we choose a different value
        if options:
            value = options[0]["value"]
        else:
            value = None

    return options, value


if __name__ == "__main__":
    app.run_server(debug=True)