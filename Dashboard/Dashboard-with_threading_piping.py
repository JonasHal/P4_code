import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import requests
import concurrent.futures
from pathlib import Path
from dash.dependencies import Input, Output, State
from math import ceil
from qwikidata.sparql import return_sparql_query_results
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules


app = dash.Dash(__name__)

SEARCHPAGE = ""
SEARCHENTITY = "Q314"

#List of ids with type ExteralIDs
property_label_dataframe = pd.read_csv(Path("../Data/properties.csv"))
property_label_dataframe_externalIDs = property_label_dataframe[(property_label_dataframe["Type"] == "ExternalId")]
property_label_dataframe_externalIDs.set_index(['Property'], inplace=True)
list_of_ids = property_label_dataframe_externalIDs.index.tolist()

#Functions utilized in the dashboard

def retrieve_properties(item):
    # Props er tom så vi ikke får references med også
    URL = "https://www.wikidata.org/w/api.php?action=wbgetclaims&entity=%s&format=json&props=" % (item)

    #Opens a HTML request session and finds the claims from one item as a list()
    with requests.Session() as S:
        try:
            DATA = dict(S.post(url=URL, headers={"user-agent": "magic browser", "Content-Type": "application/json"}).json())["claims"].keys()
            print("Retrieving properties from " + str(item) + " Succeded")
        except Exception:
            return "Item did not have any properties"

    return list(DATA)

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
    index 2 is the most frequent properties
    '''
    # Uses the two functions property_count_function() and getBooleanDF()
    df = property_count_function(property_list)
    boolean_df = getBooleanDF(property_list)

    item_count = len(property_list)
    overlap = 0.025/len(str(item_count))

    # Define the splits - the lower is the boxplot upperfence and the upper is at the number corresponding to 25 % frequency
    lower_split = round(item_count * 0.01, 0)   #Svarer til support > 0.01
    upper_split = round(item_count * 0.25, 0)  #Svarer til support > 0.25
    overlap_range = round(item_count * overlap, 0)  #Svarer til 1-9: 0.025, 10-99: 0.0125, 100-999: 0.00625 osv.

    # Define lists of properties belonging to the partitions
    above_lower_split_overlap = df[(df['Frequency'] > lower_split + overlap_range)]  # Here is the overlap
    above_upper_split = df[df['Frequency'] > upper_split]
    below_lower_split = df[df['Frequency'] <= lower_split]
    below_upper_split = df[df['Frequency'] <= upper_split]

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

def filter_suggestions(rules, item):
    suggestions = rules.copy()
    for i in suggestions.index:
        # Checks if the consequent already exists in the item. If yes, the rule is dropped.
        if suggestions['consequents'][i][0] in item:
            suggestions.drop([i], inplace=True)

    for j in suggestions.index:
        # Checks if all properties in the item is contained in each list of antecedents from the rules.
        # If no, the rule is dropped.
        if all(prop in item for prop in list(suggestions['antecedents'][j])) == False:
            suggestions.drop([j], inplace=True)

    return suggestions

#Dashboard Skeleton

#The HTML behind the dashboard
app.layout = html.Div([
    html.H1(children="Search Bar"),

    html.Div([
        dcc.Input(id="input-1", type="text", value=SEARCHENTITY),
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

#App Callback functionalities on the Dashboard

#Search bar
@app.callback(
    Output("search-output", "children"),
    Input("input-1", "value"),
)
def update_output(input1):
    #Whenever the user types something in the searchbar open a session
    if len(input1) >= 1:
        # The string with API wbsearchentities to suggestions to the user input
        URL = "https://www.wikidata.org/w/api.php?action=wbsearchentities&search=%s" \
              "&format=json&limit=5&formatversion=2&language=en" % (input1)
        with requests.Session() as S:
            DATA = S.post(url=URL, headers={"user-agent": "magic browser", "Content-Type": "application/json"}).json()

        #Whenever a search entity is returned, do something
        if len(DATA["search"]) >= 1:
            #Go through the DATA.json and append an entity label, id and description to a option list
            option_list = []
            for option in DATA["search"]:
                temp_str = ""

                try:
                    temp_str += option["id"] + "|"
                except Exception:
                    temp_str += "|"

                try:
                    temp_str += option["label"] + "|"
                except Exception:
                    temp_str += "|"

                try:
                    temp_str += option["description"]
                except Exception:
                    ""

                option_list.append(temp_str)

            #Creates a list with the suggested entities
            return html.Ul([html.Li(temp_str) for temp_str in option_list])

        #If no results is returned do something
        else:
            return "No results could be found"

    #Do nothing when no input
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
    #Everytime the user clicks "New Filter" a add a dropdown to the properties container
    new_dropdown = dcc.Dropdown(
            id={
                'type': 'property_filter-dropdown',
                'index': n_clicks
            },
            options=[{"label": i, "value": i} for i in ["P31", "P27", "P51", "P69", "P420"]],
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
    # Everytime the user clicks "New Filter" a add a dropdown to the values container
    new_dropdown = dcc.Dropdown(
            id={
                'type': 'values_filter-dropdown',
                'index': n_clicks
            },
            options=[{"label": i, "value": i} for i in ["Q3918", "Q146", "Q35872", "Q5107", "Q40218", "Q198", "Q35", "Q5"]],
            placeholder="No Value",
            style={"margin-top": "5px"}
        )
    children.append(new_dropdown)
    return children

@app.callback(
    Output("suggestion-output", "children"),
    Input("find-suggestions", "n_clicks"),
    Input("properties-output", "children"),
    State("properties_dropdown-container", "children"),
    State("values_dropdown-container", "children")
)
def find_suggestions(n_clicks, item_properties, properties, values):
    #Whenever the user clicks the "Get Suggestions" button, do something
    if n_clicks >= 1:
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
        item_list = []
        for result in results["results"]["bindings"]:
            item_list.append(result['item']['value'].split("/")[-1])

        item_list_len = len(item_list)

        #Check if this step is fulfilled
        print("The length of the item list is " + str(item_list_len))

        #The limit is set to meet the requirements of the wikibase API wbgetentities (max 50)
        #Ceil makes sure that the each subset from item_list is no longer than 50
        limit = ceil(item_list_len / 50)
        piped_list = []

        #Seperates the item_list to a nested_list with max 50 items in each list
        for pipe in range(limit):
            piped_list.append(item_list[pipe::limit])

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
        if len(str(item_list_len)) <= 4:
            lower_rel_support = (len(str(item_list_len)) - 1) / item_list_len
        else:
            lower_rel_support = (len(str(item_list_len)) + 1) / item_list_len

        #Define the min_support according to len of item_list
        if item_list_len <= 10:
            middle_rel_support = 0.15 #Means that if there are less than 7 items, every property set is mapped once
        elif item_list_len <= 28:
            middle_rel_support = 0.1 #Means that if there are less than 10 items, every property set is mapped once
        elif item_list_len <= 120:
            middle_rel_support = 0.036 #Means that if there are less than 28 items, every property set is mapped once
        else:
            middle_rel_support = 0.0085 #Means that if there are less than 120 items, every property set is mapped once

        print(item_properties)

        # Find the Frequent_items and mine rules on the lower partition, if there are more than 28 itemsets
        if item_list_len > 28:
            frequent_items_lower = fpgrowth(BooleanDFs[0], max_len=3, min_support=lower_rel_support, use_colnames=True)
            print("Lower:")
            lower_rules = mineAssociationRules(frequent_items_lower)
            lower_suggestions = filter_suggestions(lower_rules, item_properties)
            print(lower_suggestions)

        # Find the Frequent_items and mine rule on the middle partition
        frequent_items_middle = fpgrowth(BooleanDFs[1], max_len=3, min_support=middle_rel_support,
                                         use_colnames=True)
        print("Middle:")
        middle_rules = mineAssociationRules(frequent_items_middle)
        middle_suggestions = filter_suggestions(middle_rules, item_properties)
        print(middle_suggestions)

        # Find the support of the upper partition
        frequent_items_upper = fpgrowth(BooleanDFs[2], max_len=1, min_support=0.25, use_colnames=True)
        frequent_items_upper = removeExternalIdsSingle(frequent_items_upper, "itemsets")

        print(frequent_items_upper)

        print("Upper:")
        print('The suggestions consist of {} unique properties'.format(len(frequent_items_upper)))

        print("Everything Done")

    else:
        return ""
if __name__ == '__main__':
    app.run_server(debug=True)