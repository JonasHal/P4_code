import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import itertools
import requests
import concurrent.futures
import time
import sys
from pickle import dumps
from SPARQLWrapper import SPARQLWrapper, JSON
from pathlib import Path
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, MATCH
from math import ceil
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
import webbrowser
from threading import Timer

app = dash.Dash(__name__, suppress_callback_exceptions=True)

SEARCHPAGE = ""

# List of ids with type ExteralIDs
property_label_dataframe = pd.read_csv(Path("../Data/properties.csv"))
property_label_dataframe_externalIDs = property_label_dataframe[(property_label_dataframe["Type"] == "ExternalId")]
property_label_dataframe_externalIDs.set_index(['Property'], inplace=True)
list_of_ids = property_label_dataframe_externalIDs.index.tolist()

# Functions utilized in the dashboard
def get_results(query):
    """
    Sends a request to the Wikidata SPARQL query tool and receives the data in JSON format
    :param query: A SPARQL query, that works on Wikidata SPARQL tool
    :return: The query with JSON format
    """
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def searchWikidata(input, type):
    """
    Sends a request to the Wikidata API and transform the data from JSON into a list
    that has been formatted like "label ("id") | "description
    :param input: The user input in the text field
    :param type: Specifies which entities to search for: Either "item" or "property"
    :return: The results from the API action=wbsearchentities as HTML.li in a HTML.Ul
    """
    # Whenever the user types something in the searchbar open a session
    if len(input) >= 1:
        # The string with API wbsearchentities to suggestions to the user input
        URL = "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=%s" \
              "&format=json&limit=5&formatversion=2&language=en&type=%s" % (input, type)
        with requests.Session() as S:
            DATA = S.post(url=URL, headers={"user-agent": "magic browser", "Content-Type": "application/json"}).json()

        # Whenever a search entity is returned, do something
        if len(DATA["search"]) >= 1:
            # Go through the DATA.json and append an entity label, id and description to a option list
            option_list = []
            for option in DATA["search"]:
                temp_str = ""

                try:
                    temp_str += option["label"] + " ("
                except Exception:
                    temp_str += "("

                try:
                    temp_str += option["id"] + ")"
                except Exception:
                    temp_str += ")"

                temp_json = {"label": temp_str, "value": option["id"]}

                option_list.append(temp_json)

            # Creates a list with the suggested entities
            return option_list

        # If no results is returned do nothing
        else:
            return []

    # Do nothing when no input
    else:
        return []


def retrieve_properties_piped(item_list):
    """
    Sends a request to the Wikidata API and transform the data from JSON into a dictionary to
    extract the claims each property has.
    :param item_list: A list with up to 50 wikidata items written with Q-code
    :return: A nested list, with all the properties each item has
    """
    # Creates the query by seperating each item with "|"
    item_list_query = ""
    for item in range(len(item_list)):
        if item == (len(item_list) - 1):
            item_list_query += item_list[item]
        else:
            item_list_query += item_list[item] + "%7C"

    # The string with API wbgetentities to find multiple items in an optimal format
    URL = "https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids=%s&props=claims&languages=en&formatversion=2" % (
        item_list_query)

    # Opens a HTMl session and gets the DATA from the API
    with requests.Session() as S:
        DATA = dict(S.post(url=URL, headers={"user-agent": "magic browser", "Content-Type": "application/json"}).json())

    # Appends the properties of each item to a nested list
    nested_list = []
    for entity in DATA["entities"]:
        try:
            nested_list.append(list(DATA["entities"][entity]["claims"].keys()))
        except:
            pass

    return nested_list


def getBooleanDF(property_list):
    """
    Transform the nested list into a boolean dataframe with transactions on rows and items on columns
    :param property_list: The nested list with the wikidata properties
    :return: A boolean dataframe
    """
    te = TransactionEncoder()
    te_ary = te.fit(property_list).transform(property_list)
    boolean_dataframe = pd.DataFrame(te_ary, columns=te.columns_)
    return boolean_dataframe


def property_count_function(listOfProperties):
    """
    Counts the frequency of each property
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


def splitNestedListToBooleanDFs(property_list):
    '''
    Takes a nested list from all the retrieve_properties_piped() outputs and partition the data
    :param property_list: Input is the nested property list extracted from extractProperties()
    :return: a list of in total 3 dataframes. Index 0 is the "rarest" properties, index 1 is the middle properties and
    index 2 is the most frequent properties. If the len of the property list is less than 28, The rare properties wont exist and
    would not return anything.
    '''
    # Uses the two functions property_count_function() and getBooleanDF()
    df = property_count_function(property_list)
    boolean_df = getBooleanDF(property_list)
    print("Unique Properties for this query: " + str(len(df)))

    item_count = len(property_list)
    overlap = 0.025 / len(str(item_count))

    # Define the splits - the lower is 0.01 + overlap and the upper is at the number corresponding to 25 % frequency
    lower_split = round(item_count * 0.01, 0)  # Support > 0.01
    upper_split = round(item_count * 0.25, 0)  # Support > 0.25
    overlap_range = round(item_count * overlap, 0)  # Same as til 10-99: 0.0125, 100-999: 0.00625 etc.

    # Define lists of properties belonging to the partitions
    above_lower_split_overlap = df[(df['Frequency'] > lower_split + overlap_range)]  # Lower, Here is the overlap
    above_upper_split = df[df['Frequency'] > upper_split]  # Middle
    below_lower_split = df[df['Frequency'] <= lower_split]  # Middle
    below_upper_split = df[df['Frequency'] <= upper_split]  # Upper

    # Drops the relevant list of properties from the original boolean dataframe thereby creating the partitioned datasets
    split_df_lower = boolean_df.drop(above_lower_split_overlap['Property'].tolist(), axis='columns')
    split_df_middle = boolean_df.drop(below_lower_split['Property'].tolist() + above_upper_split['Property'].tolist(),
                                      axis='columns')
    split_df_upper = boolean_df.drop(below_upper_split['Property'].tolist(), axis='columns')

    return split_df_lower, split_df_middle, split_df_upper


def removeExternalIdsSingle(rule_df, column):
    """
    Function used to remove properties of type ExternalId from a given column
    :param rule_df: The rules mined from the function mineAssociationRules()
    :param column: Specifies which column to remove ExternalIds from
    :return: The dataframe with the rules without properties of type ExternalId in a given column
    """
    rule_df[column] = [list(rule_df[column][i]) for i in rule_df.index]

    for i in rule_df.index:
        if rule_df[column][i][0] in list_of_ids:
            rule_df = rule_df.drop([i])

    return rule_df


def countUniqueConsequents(rule_df):
    """
    Function used to count unique properties that gets recommeded for that partition
    :param rule_df: The dataframe created from running the association_rules() function from mlxtend package.
    :return: The unique consequences that has been found after rule mining.
    """
    unique_consequents = []
    for i in rule_df.index:
        if rule_df['consequents'][i][0] not in unique_consequents:
            unique_consequents.append(rule_df['consequents'][i][0])

    return unique_consequents


def mineAssociationRules(frequent_items):
    """
    Mines Association Rules, counts the consequents, removes ExternalIds and counts unique consequents.
    :param frequent_items: The frequent itemsets found using FP-Growth algorithm
    :return:
    """
    # Uses the package mlxtend to mine rules
    rules = association_rules(frequent_items, metric="confidence", min_threshold=0.99)

    # Define and locate the rules with only 1 consequent
    rules["consequent_len"] = rules["consequents"].apply(lambda x: len(x))
    rules = rules[(rules['consequent_len'] == 1) & (rules['lift'] > 1) & (rules['leverage'] > 0)]

    # Changes the datatype of the consequents from frozenset, which is immutable, to a list.
    rules = removeExternalIdsSingle(rules, "consequents")

    unique_consequents = countUniqueConsequents(rules)
    print('The rules consist of {} unique consequents'.format(len(unique_consequents)))

    return rules


def filter_suggestions(rules, item):
    """
    Filters the suggestions based on the user input of the item that the user has specified.
    This function is used on the mined association rules
    :param rules: The rules retrieved from the function mineAssociationRules()
    :param item: The properties of a wikidata item. This is the output from extract_properties()
    :return: A list of suggestions
    """
    suggestions = rules.copy()
    for i in suggestions.index:
        # Checks if the consequent already exists in the item. If yes, the rule is dropped.
        if suggestions['consequents'][i][0] in item:
            suggestions.drop([i], inplace=True)

    for j in suggestions.index:
        # For every list of properties in the antecedents, check if they are contained in item properties list
        # If no, the rule is dropped.
        if all(props in item for props in list(suggestions['antecedents'][j])) == False:
            suggestions.drop([j], inplace=True)

    result = np.unique([*itertools.chain.from_iterable(suggestions.consequents)]).tolist()

    return result


def upper_properties(upper, item):
    """
    Filters the suggestions based on the user input of the item that the user has specified.
    This function is used on the properties without association rule mining.
    :param upper: The upper partition (as this is the only partition where we dont rule mine)
    :param item: The properties of a wikidata item. This is the output from extract_properties()
    :return: A list of suggestions
    """
    result = []
    for [prop] in upper.itemsets:
        if prop not in item:
            result.append(prop)

    return result


# Dashboard Skeleton

# The HTML behind the dashboard
app.layout = html.Div([
    html.H1("Wikidata Property Suggester", id="title",
            style={"grid-column": "1 / span 4", "text-align": "center"}
            ),

    html.Div([
        html.H2(children="Investigate Item"),
        html.P(children="Input the items Q-code you want to investigate:"),

        html.Div([
            dcc.Dropdown(id="investigate_item"),
            html.Div(id="properties-output", style={"display": "none"}),
            html.Div(id="investigate_item-confirmed")
        ]),

        html.H2(children="Input Properties To Filter On"),

        html.Div([
            html.Button("Add Filter", id="add-filter", n_clicks=0,
                        style={"grid-column": "1 / span 2"}
                        ),
            html.Div(id="properties_dropdown-container", children=[],
                     style={"width": "220px"}
                     ),
            html.Div(id="values_dropdown-container", children=[],
                     style={"width": "220px"}
                     ),
            html.Div(id="dropdown-container-output")
        ], style={"display": "inline-grid",
                  "grid-gap": "24px",
                  "grid-template-columns": "auto auto",
                  "margin-right": "auto",
                  "margin-left": "auto",
                  "width": "8em"}
        ),

        html.Div([
            html.Button("Get Suggestions", id="find-suggestions", n_clicks=0),
            dcc.Loading(
                type="circle",
                children=[html.Div(id="loading-output")])
        ])
    ]),

    html.Div([
        html.H3(children="General Properties"),
        html.Div([html.Span(
                    "Disclaimer",
                    id="tooltip-target",
                    style={"color": "blue", "cursor": "pointer"},
                ),
            dbc.Tooltip("If the property filters are very broad, "
                                     "some of these general properties will not make sense in every context.",
                        target="tooltip-target",
                        style={"background-color": "#f0f0f5",
                               "text-align": "center",
                               "width": "200px"})
        ]),
        html.Div(id="upper_suggestion-container")
    ]),

    html.Div([
        html.H3(children="Occasional Properties"),
        html.Div(id="middle_suggestion-container")

    ]),

    html.Div([
        html.H3(children="Rare Properties"),
        html.Div(id="lower_suggestion-container")
    ]),

], style={"display": "inline-grid",
          "grid-gap": "1%",
          "grid-template-columns": "auto auto auto auto",
          "width": "94%",
          "margin-left": "3%",
          "margin-right": "3%"}
)

# App Callback functionalities on the Dashboard

# Search bar
@app.callback(
    Output("investigate_item", "options"),
    [Input("investigate_item", "search_value")],
)
def update_output(input):
    if not input:
        raise PreventUpdate
    return searchWikidata(input, "item")

# Bruger mediawiki API wbgetclaims til at hente claims fra en item
@app.callback(
    Output("properties-output", "children"),
    Output("investigate_item-confirmed", "children"),
    Input("investigate_item", "value"),
)
def extract_properties(item):
    # Props is empty, so the references are not included
    URL = "https://www.wikidata.org/w/api.php?action=wbgetclaims&entity=%s&format=json&props=" % (item)

    # Opens a HTML request session and finds the claims from one item as a list()
    with requests.Session() as S:
        try:
            DATA = \
                dict(S.post(url=URL,
                            headers={"user-agent": "magic browser", "Content-Type": "application/json"}).json())[
                    "claims"].keys()
        except Exception:
            return [], "Item: " + str(item) + " did not have any properties"

    return list(DATA), ("Properties have been extracted from " + str(item))


# Properties and Values Input: https://dash.plotly.com/dash-core-components/dropdown (Dynamic Options)
@app.callback(
    Output("properties_dropdown-container", "children"),
    Input("add-filter", "n_clicks"),
    State('properties_dropdown-container', 'children'),
)
def input_properties(n_clicks, children):
    # Everytime the user clicks "New Filter" a add a dropdown to the properties container
    new_dropdown = dcc.Dropdown(
        id={
            'type': 'property_filter-dropdown',
            'index': n_clicks
        },
        options=[],
        placeholder="Select a Property...",
        style={"margin-top": "5px"}
    )
    children.append(new_dropdown)
    return children


@app.callback(
    Output("values_dropdown-container", "children"),
    Input("add-filter", "n_clicks"),
    State('values_dropdown-container', 'children'),
)
def input_values(n_clicks, children):
    # Everytime the user clicks "New Filter" a add a dropdown to the values container
    new_dropdown = dcc.Dropdown(
        id={
            'type': 'values_filter-dropdown',
            'index': n_clicks,
        },
        options=[],
        placeholder="No Value",
        style={"margin-top": "5px"}
    )
    children.append(new_dropdown)
    return children

@app.callback(
    Output({'type': "property_filter-dropdown", 'index': MATCH}, "options"),
    [Input({'type': "property_filter-dropdown", 'index': MATCH}, "search_value")],
)
def update_output(input):
    if not input:
        raise PreventUpdate
    return searchWikidata(input, "property")

@app.callback(
    Output({'type': "values_filter-dropdown", 'index': MATCH}, "options"),
    [Input({'type': "values_filter-dropdown", 'index': MATCH}, "search_value")],
)
def update_output(input):
    if not input:
        raise PreventUpdate
    return searchWikidata(input, "item")

@app.callback(
    Output("upper_suggestion-container", "children"),
    Output("middle_suggestion-container", "children"),
    Output("lower_suggestion-container", "children"),
    Output("find-suggestions", "n_clicks"),
    Output("loading-output", "children"),
    Input("find-suggestions", "n_clicks"),
    Input("properties-output", "children"),
    State("properties_dropdown-container", "children"),
    State("values_dropdown-container", "children")
)
def find_suggestions(n_clicks, item_properties, properties, values):
    # Whenever the user clicks the "Get Suggestions" button, do something
    if n_clicks == 1:
        # Creates the SPARQL query from the filters
        filters = ""
        for i in range(len(properties)):
            try:
                # Extracts the property and property value from the filter and add to the query
                temp_property = properties[i]['props']['value']
                temp_value = values[i]['props']['value']
                filters += "?item wdt:" + temp_property + " wd:" + temp_value + " . "
            except:
                try:
                    # Extracts the property from the filter, but sets property as a variable and add to the query
                    temp_property = properties[i]['props']['value']
                    temp_value = "?variable" + str(i + 1)
                    filters += "?item wdt:" + temp_property + temp_value + " . "
                except:
                    # If nothing is in the input, move on
                    pass

        # Create the SPARQL query and run it on wikidata
        query_string = """ SELECT ?item WHERE {""" + filters + """}"""
        results = get_results(query_string)

        # Takes the results from the SPARQL query and append the wikibase value to the item_list
        item_list = [result['item']['value'].split("/")[-1] for result in results["results"]["bindings"]]
        item_list_len = len(item_list)

        # Check if this step is fulfilled
        print("The length of the item list is " + str(item_list_len))
        if item_list_len == 0:
            raise PreventUpdate

        # The limit is set to meet the requirements of the wikibase API wbgetentities (max 50)
        # Ceil makes sure that the each subset from item_list is no longer than 50
        limit = ceil(item_list_len / 50)

        # Seperates the item_list to a nested_list with max 50 items in each list
        piped_list = [item_list[pipe::limit] for pipe in range(limit)]

        loading_bar_progress = 0
        nested_list = []

        # Utilizes threading to send multiple HTML requests at once
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submits each subset of the item_list to the function retrieve_properties_piped
            future_nested_list = {executor.submit(retrieve_properties_piped, items): items for items in piped_list}
            # Whenever the HTML request completes, run the iteration in the for-loop
            for future in concurrent.futures.as_completed(future_nested_list):
                # Since the return is a nested list already, extend() adds the individual property_lists to the nested_list
                nested_list.extend(future.result())
                # Loadingbar to follow the progress in the console
                loading_bar_progress += 1
                print(str(loading_bar_progress) + " / " + str(limit))

        # Partitioning Part
        BooleanDFs = splitNestedListToBooleanDFs(nested_list)

        start = time.perf_counter()
        # Find the Frequent_items and mine rules on the lower partition, if there are more than 44 itemsets
        if item_list_len > 44:
            # Define the lower_min_support according to len of item_list
            if len(str(item_list_len)) <= 3:
                lower_rel_support = (len(str(
                    item_list_len)) - 1) / item_list_len  # From 44-99 every pair is included in the Frequent Items
                # From 100-999 every pair that appears twice are included
            elif len(str(item_list_len)) == 4:
                lower_rel_support = 4 / item_list_len  # From 1000-9999 every pair that appears 4 times are included
            else:
                lower_rel_support = (len(str(
                    item_list_len)) + 1) / item_list_len  # From 10000-99999 every pair that appears 6 times are included

            print("Lower:")
            frequent_items_lower = fpgrowth(BooleanDFs[0], max_len=3, min_support=lower_rel_support, use_colnames=True)
            print(len(frequent_items_lower))
            lower_rules = mineAssociationRules(frequent_items_lower)
            lower_suggestions = filter_suggestions(lower_rules, item_properties)
        else:
            lower_suggestions = ["Not enough items to search for rare properties"]

        # Define the middle_min_support according to len of item_list
        if item_list_len <= 9:
            middle_rel_support = 1 / item_list_len  # Means that if there are less than 10 items, every property set should appear once
        elif item_list_len <= 120:
            middle_rel_support = 2 / item_list_len  # Means that if there are less than 121 items, every property set should appear twice
        else:
            middle_rel_support = 0.0084

        # Find the Frequent_items and mine rule on the middle partition
        print("Middle:")
        frequent_items_middle = fpgrowth(BooleanDFs[1], max_len=3, min_support=middle_rel_support, use_colnames=True)
        print(len(frequent_items_middle))
        middle_rules = mineAssociationRules(frequent_items_middle)
        middle_suggestions = filter_suggestions(middle_rules, item_properties)

        # Find the support of the upper partition
        print("Upper:")
        frequent_items_upper = fpgrowth(BooleanDFs[2], max_len=1, min_support=0.25, use_colnames=True)
        frequent_items_upper = removeExternalIdsSingle(frequent_items_upper, "itemsets")
        print(len(frequent_items_upper))
        upper_suggestions = upper_properties(frequent_items_upper, item_properties)

        print("Everything Done")
        stop = time.perf_counter()
        print("The execution time of FP-Growth and rule mining is: " + str(stop - start))

        return html.Ul([html.Li(dcc.Link(href="https://www.wikidata.org/wiki/Property:" + prop,
                                         children=prop, target='_blank')) for prop in upper_suggestions]), \
               html.Ul([html.Li(dcc.Link(href="https://www.wikidata.org/wiki/Property:" + prop,
                                         children=prop, target='_blank')) for prop in middle_suggestions]), \
               html.Ul([html.Li(dcc.Link(href="https://www.wikidata.org/wiki/Property:" + prop,
                                         children=prop, target='_blank')) for prop in lower_suggestions]), \
               0, ""

    else:
        return [], [], [], 0, ""

if __name__ == '__main__':
    app.run_server(debug=True)
