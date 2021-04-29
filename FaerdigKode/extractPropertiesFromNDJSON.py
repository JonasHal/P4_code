import ndjson
import pandas as pd
from pathlib import Path

def extractItemCodes(filename):
    """
    Takes an NDJSON file and finds the list with the ItemCodes
    :param filename: What file to open: for example Path("Data/universities_latest_all.ndjson")
    :return: returns a Python list with all the properties from the NDJSON file.
    """

    item_list = []

    with open(filename, encoding="utf-8") as f:
        wikidata = ndjson.load(f)

    wikidata_df = pd.DataFrame(wikidata)

    # Walks the .ndjson file and extracts the properties
    for i in range(len(wikidata_df)):
        item_list.append(wikidata_df["id"][i])

    return item_list

def extractProperties(filename):
    """
    Walks through an NDJSON file and makes a nested list, with all the properties for each item in a subset of wikidata
    :param filename: What file to open: for example Path("Data/universities_latest_all.ndjson")
    :return: returns a Python list with all the properties from the NDJSON file.
    """

    property_list = []

    with open(filename, encoding="utf-8") as f:
        wikidata = ndjson.load(f)

    wikidata_df = pd.DataFrame(wikidata)

    # Walks the .ndjson file and extracts the properties
    for i in range(len(wikidata_df)):
        property_list.append(list(wikidata_df["claims"][i].keys()))

    return property_list


def replacePcodesWithPlabels(listofproperties, external_ids = True):
    """
    Replace P-values with P-labels
    :param listofproperties: Input the nested list from the extractProperties function
    :return: listofproperties_with_labels: A new list containing the same data as the original nested list
    only the P-codes are replaced with the P-label values from Wikidata.
    """
    # Converts the csv file containing P-codes and P label values to a dataframe
    property_label_dataframe = pd.read_csv(Path("../Data/properties.csv"))
    property_label_dataframe.set_index(['Property'], inplace=True)

    listofproperties_with_labels = []

    if external_ids == True:
        for nested_list in listofproperties:
            prop_list = []
            for prop in nested_list:
                try:
                    prop_label_value = property_label_dataframe.loc[prop,].Value
                    prop_list.append(prop_label_value)
                except :
                    print("The P-code does not exist in the property_label_dataframe")

            listofproperties_with_labels.append(prop_list)

    elif external_ids == False:
        property_label_dataframe = property_label_dataframe[(property_label_dataframe["Type"] != "ExternalId")]
        for nested_list in listofproperties:
            prop_list = []
            for prop in nested_list:
                try:
                    prop_label_value = property_label_dataframe.loc[prop,].Value
                    prop_list.append(prop_label_value)
                except:
                    pass

    else:
        return print("Error: Please enter boolean value for external_ids")

    return listofproperties_with_labels


def convertPropertyListToTXT(property_list, output_filename):
    """
    Extracts a nested list of properties to a text file
    :param property_list: Nested list of properties
    :param output_filename: Name of the output file to write to
    :return: nothing
    """
    with open(output_filename, 'w') as f:
        for nested_lists in property_list:
            try:
                int_list = [int(list[1:]) for list in nested_lists]
                string_list = str(int_list).replace('[', '{').replace(']', '}')
                f.write(string_list)
                f.write("\n")
            except TypeError:
                print('The type of data is wrong')
        f.close()

if __name__ == '__main__':
    property_list = extractProperties(Path("../Data/universities_latest_all.ndjson"))
    property_list_with_labels = replacePcodesWithPlabels(property_list, external_ids=False)

    #convertPropertyListWithLabelsToTXT(property_list_with_labels, 'test.txt')

    #convertPropertyListToTXT(property_list, '../Users/Magnus/transaction.txt')