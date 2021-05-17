import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import itertools
import requests
import concurrent.futures
from pathlib import Path
from dash.dependencies import Input, Output, State
from math import ceil
from qwikidata.sparql import return_sparql_query_results
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules


app = dash.Dash(__name__, suppress_callback_exceptions = True)

SEARCHPAGE = ""

#List of ids with type ExteralIDs
property_label_dataframe = pd.read_csv(Path("../Data/properties.csv"))
property_label_dataframe_externalIDs = property_label_dataframe[(property_label_dataframe["Type"] == "ExternalId")]
property_label_dataframe_externalIDs.set_index(['Property'], inplace=True)
list_of_ids = property_label_dataframe_externalIDs.index.tolist()

#Functions utilized in the dashboard

def searchWikidata(input, type):
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
                    temp_str += "|"

                try:
                    temp_str += option["id"] + ") | "
                except Exception:
                    temp_str += "|"

                try:
                    temp_str += option["description"]
                except Exception:
                    ""

                option_list.append(temp_str)

            # Creates a list with the suggested entities
            return html.Ul([html.Li(temp_str) for temp_str in option_list])

        # If no results is returned do something
        else:
            return "No results could be found"

    # Do nothing when no input
    else:
        return ""

def retrieve_properties_piped(item_list):
    #Creates the query by seperating each item with "|"
    item_list_query = ""
    for item in range(len(item_list)):
        if item == (len(item_list) - 1):
            item_list_query += item_list[item]
        else:
            item_list_query += item_list[item] + "%7C"

    #The string with API wbgetentities to find multiple items in an optimal format
    URL = "https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids=%s&props=claims&languages=en&formatversion=2" % (item_list_query)

    #Opens a HTMl session and gets the DATA from the API
    with requests.Session() as S:
        DATA = dict(S.post(url=URL, headers={"user-agent": "magic browser", "Content-Type": "application/json"}).json())

    #Appends the properties of each item to a nested list
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

    :param property_list: Input is the nested property list extracted from extractProperties()
    :return: a list of in total 3 dataframes. Index 0 is the "rarest" properties, index 1 is the middle properties and
    index 2 is the most frequent properties. If the len of the property list is less than 28, The rare properties wont exist and
    would not return anything.
    '''
    # Uses the two functions property_count_function() and getBooleanDF()
    df = property_count_function(property_list)
    boolean_df = getBooleanDF(property_list)

    item_count = len(property_list)
    overlap = 0.025/len(str(item_count))

    # Define the splits - the lower is 0.01 + overlap and the upper is at the number corresponding to 25 % frequency
    lower_split = round(item_count * 0.01, 0)   #Support > 0.01
    upper_split = round(item_count * 0.25, 0)  #Support > 0.25
    overlap_range = round(item_count * overlap, 0)  #Same as til 10-99: 0.0125, 100-999: 0.00625 etc.

    # Define lists of properties belonging to the partitions
    above_lower_split_overlap = df[(df['Frequency'] > lower_split + overlap_range)]  #Lower, Here is the overlap
    above_upper_split = df[df['Frequency'] > upper_split] #Middle
    below_lower_split = df[df['Frequency'] <= lower_split] #Middle
    below_upper_split = df[df['Frequency'] <= upper_split] #Upper

    # Drops the relevant list of properties from the original boolean dataframe thereby creating the partitioned datasets
    split_df_lower = boolean_df.drop(above_lower_split_overlap['Property'].tolist(), axis='columns')
    split_df_middle = boolean_df.drop(below_lower_split['Property'].tolist() + above_upper_split['Property'].tolist(), axis='columns')
    split_df_upper = boolean_df.drop(below_upper_split['Property'].tolist(), axis='columns')

    return split_df_lower, split_df_middle, split_df_upper

def countUniqueConsequents(rule_df):
    unique_consequents = []
    for i in rule_df.index:
        if rule_df['consequents'][i][0] not in unique_consequents:
            unique_consequents.append(rule_df['consequents'][i][0])

    return unique_consequents

def removeExternalIdsSingle(dfWithFrozenset, column):
    dfWithFrozenset[column] = [list(dfWithFrozenset[column][i]) for i in dfWithFrozenset.index]

    for i in dfWithFrozenset.index:
        if dfWithFrozenset[column][i][0] in list_of_ids:
            dfWithFrozenset = dfWithFrozenset.drop([i])

    return dfWithFrozenset

def mineAssociationRules(frequent_items):
    #Uses the package mlxtend to mine rules
    rules = association_rules(frequent_items, metric="confidence", min_threshold=0.99)

    #Define and locate the rules with only 1 consequent
    rules["consequent_len"] = rules["consequents"].apply(lambda x: len(x))
    rules = rules[(rules['consequent_len'] == 1) & (rules['lift'] > 1) &(rules['leverage'] > 0)]

    # Changes the datatype of the consequents from frozenset, which is immutable, to a list.
    rules = removeExternalIdsSingle(rules, "consequents")

    unique_consequents = countUniqueConsequents(rules)
    print('The rules consist of {} unique consequents'.format(len(unique_consequents)))

    return rules


def upper_properties(upper, item):
    result = []
    for [prop] in upper.itemsets:
        if prop not in item:
            result.append(prop)

    return result

def filter_suggestions(rules, item):
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

#Dashboard Skeleton

#The HTML behind the dashboard
app.layout = html.Div([
    html.H1("Wikidata Property Suggester", id="title",
                        style={"grid-column": "1 / span 4", "text-align": "center"}
                        ),

    html.Div([
        html.H2(children="Investigate Item"),
        html.P(children="Input the items Q-code you want to investigate:"),

        html.Div([
            dcc.Input(id="investigate_item", type="text", debounce=True),
            html.Div(id="properties-output", style={"display": "none"}),
            html.Div(id="investigate_item-confirmed")
        ]),

        html.H2(children="Input Properties To Filter On"),

        html.Div([
            html.Button("Add Filter", id="add-filter", n_clicks=0,
                        style={"grid-column": "1 / span 2"}
                        ),
            html.Div(id="properties_dropdown-container", children=[],
                     style={"width": "160px"}
                     ),
            html.Div(id="values_dropdown-container", children=[],
                     style={"width": "160px"}
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
            html.Button("Get Suggestions", id="find-suggestions", n_clicks=0)
        ])
    ]),

    html.Div([
        html.H3(children="General Properties"),
        html.Div([html.Span(
                    "Disclaimer",
                    id="tooltip-target",
                    style={"color": "blue", "cursor": "pointer"},
                ),
            dbc.Tooltip("If the propety filters are very broad, "
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

    html.Div([
        html.Div([
            html.H4(children="Search entities"),
            dcc.Input(id="entities-input", type="text", value=SEARCHPAGE),
            html.Div(id="item_search-output")
        ]),

        html.Div([
            html.H4(children="Search properties"),
            dcc.Input(id="properties-input", type="text", value=SEARCHPAGE),
            html.Div(id="property_search-output")
        ]),
    ], style={"grid-column": "1 / span 4",
              "display": "inline-grid",
              "grid-gap": "40px",
              "grid-template-columns": "auto auto"}
    )

], style={"display": "inline-grid",
          "grid-gap": "1%",
          "grid-template-columns": "auto auto auto auto",
          "width":"94%",
          "margin-left": "3%",
          "margin-right": "3%"}
)

#App Callback functionalities on the Dashboard

#Search bar
@app.callback(
    Output("item_search-output", "children"),
    Input("entities-input", "value"),
)
def update_output(input):
    return searchWikidata(input, "item")

@app.callback(
    Output("property_search-output", "children"),
    Input("properties-input", "value"),
)
def update_output(input):
    return searchWikidata(input, "property")

#Bruger mediawiki API wbgetclaims til at hente claims fra en item
@app.callback(
    Output("properties-output", "children"),
    Output("investigate_item-confirmed", "children"),
    Input("investigate_item", "value"),
)
def extract_properties(item):
    # Props er tom så vi ikke får references med også
    URL = "https://www.wikidata.org/w/api.php?action=wbgetclaims&entity=%s&format=json&props=" % (item)

    # Opens a HTML request session and finds the claims from one item as a list()
    with requests.Session() as S:
        try:
            DATA = \
            dict(S.post(url=URL, headers={"user-agent": "magic browser", "Content-Type": "application/json"}).json())[
                "claims"].keys()
        except Exception:
            return [], "Item: " + str(item) + " did not have any properties"

    return list(DATA), ("Properties have been extracted from " + str(item))

#Properties and Values Input: https://dash.plotly.com/dash-core-components/dropdown (Dynamic Options)
@app.callback(
    Output("properties_dropdown-container", "children"),
    Input("add-filter", "n_clicks"),
    State('properties_dropdown-container', 'children'),
)
def input_properties(n_clicks, children):
    #Everytime the user clicks "New Filter" a add a dropdown to the properties container
    new_input = dcc.Input(
            id={
                'type': 'property_filter-dropdown',
                'index': n_clicks
            },
            size="22.5",
            placeholder = "Select a Property...",
            style={"margin-top": "10px"}
        )
    children.append(new_input)
    return children

@app.callback(
    Output("values_dropdown-container", "children"),
    Input("add-filter", "n_clicks"),
    State('values_dropdown-container', 'children'),
)
def input_values(n_clicks, children):
    # Everytime the user clicks "New Filter" a add a dropdown to the values container
    new_dropdown = dcc.Input(
            id={
                'type': 'values_filter-dropdown',
                'index': n_clicks
            },
            size="22.5",
            placeholder="No Value",
            style={"margin-top": "10px"}
        )
    children.append(new_dropdown)
    return children

@app.callback(
    Output("upper_suggestion-container", "children"),
    Output("middle_suggestion-container", "children"),
    Output("lower_suggestion-container", "children"),
    Output("find-suggestions", "n_clicks"),
    Input("find-suggestions", "n_clicks"),
    Input("properties-output", "children"),
    State("properties_dropdown-container", "children"),
    State("values_dropdown-container", "children")
)
def find_suggestions(n_clicks, item_properties, properties, values):
    #Whenever the user clicks the "Get Suggestions" button, do something
    if n_clicks == 1:
        #Creates the SPARQL query from the filters
        filters = ""
        for i in range(len(properties)):
            try:
                #Extracts the property and property value from the filter and add to the query
                temp_property = properties[i]['props']['value']
                temp_value = values[i]['props']['value']
                filters += "?item wdt:" + temp_property + " wd:" + temp_value + " . "
            except:
                try:
                    #Extracts the property from the filter, but sets property as a variable and add to the query
                    temp_property = properties[i]['props']['value']
                    temp_value = "?variable" + str(i + 1)
                    filters += "?item wdt:" + temp_property + temp_value + " . "
                except:
                    #If nothing is in the input, move on
                    pass

        #Create the SPARQL query and run it on wikidata
        query_string = """ SELECT ?item WHERE {""" +filters+"""}"""
        results = return_sparql_query_results(query_string)

        #Takes the results from the SPARQL query and append the wikibase value to the item_list
        item_list = [result['item']['value'].split("/")[-1] for result in results["results"]["bindings"]]
        item_list_len = len(item_list)

        #Check if this step is fulfilled
        print("The length of the item list is " + str(item_list_len))

        #The limit is set to meet the requirements of the wikibase API wbgetentities (max 50)
        #Ceil makes sure that the each subset from item_list is no longer than 50
        limit = ceil(item_list_len / 50)
        # Seperates the item_list to a nested_list with max 50 items in each list
        piped_list = [item_list[pipe::limit] for pipe in range(limit)]

        #Seperates the item_list to a nested_list with max 50 items in each list
        # for pipe in range(limit):
        #     piped_list.append(item_list[pipe::limit])

        loading_bar_progress = 0
        nested_list = []

        #Utilizes threading to send multiple HTML requests at once
        with concurrent.futures.ThreadPoolExecutor() as executor:
            #Submits each subset of the item_list to the function retrieve_properties_piped
            future_nested_list = {executor.submit(retrieve_properties_piped, items): items for items in piped_list}
            #Whenever the HTML request completes, run the iteration in the for-loop
            for future in concurrent.futures.as_completed(future_nested_list):
                #Since the return is a nested list already, extend() adds the individual property_lists to the nested_list
                nested_list.extend(future.result())
                #Loadingbar to follow the progress in the console
                loading_bar_progress += 1
                print(str(loading_bar_progress) + " / " + str(limit))

        #Partitioning Part
        BooleanDFs = splitNestedListToBooleanDFs(nested_list)


        # Find the Frequent_items and mine rules on the lower partition, if there are more than 28 itemsets
        if item_list_len > 28:
            # Define the lower_min_support according to len of item_list
            if len(str(item_list_len)) <= 3:
                lower_rel_support = (len(str(
                    item_list_len)) - 1) / item_list_len  # From 28-99 every pair is included in the Frequent Items
                # From 100-999 every pair that appears twice are included
            elif len(str(item_list_len)) == 4:
                lower_rel_support = (len(str(
                    item_list_len))) / item_list_len  # From 1000-9999 every pair that appears 4 times are included
            else:
                lower_rel_support = (len(str(
                    item_list_len)) + 1) / item_list_len  # From 10000-99999 every pair that appears 6 times are included

            frequent_items_lower = fpgrowth(BooleanDFs[0], max_len=3, min_support=lower_rel_support,
                                            use_colnames=True)
            lower_rules = mineAssociationRules(frequent_items_lower)
            lower_suggestions = filter_suggestions(lower_rules, item_properties)
        else:
            lower_suggestions = ["Not enough items to search for rare properties"]

        #Define the middle_min_support according to len of item_list
        if item_list_len <= 10:
            middle_rel_support = 0.15 #Means that if there are less than 7 items, every property set is mapped once
        elif item_list_len <= 28:
            middle_rel_support = 0.1 #Means that if there are less than 10 items, every property set is mapped once
        elif item_list_len <= 120:
            middle_rel_support = 0.036 #Means that if there are less than 28 items, every property set is mapped once
        else:
            middle_rel_support = 0.00836 #Means that if there are less than 120 items, every property set is mapped once

        # Find the Frequent_items and mine rule on the middle partition
        frequent_items_middle = fpgrowth(BooleanDFs[1], max_len=3, min_support=middle_rel_support, use_colnames=True)
        middle_rules = mineAssociationRules(frequent_items_middle)
        middle_suggestions = filter_suggestions(middle_rules, item_properties)

        # Find the support of the upper partition
        frequent_items_upper = fpgrowth(BooleanDFs[2], max_len=1, min_support=0.25, use_colnames=True)
        frequent_items_upper = removeExternalIdsSingle(frequent_items_upper, "itemsets")
        upper_suggestions = upper_properties(frequent_items_upper, item_properties)

        print("Everything Done")

        return html.Ul([html.Li(prop) for prop in upper_suggestions]), \
               html.Ul([html.Li(prop) for prop in middle_suggestions]), \
               html.Ul([html.Li(prop) for prop in lower_suggestions]), 0

    else:
        return [], [], [], 0


if __name__ == '__main__':
    app.run_server(debug=True)
