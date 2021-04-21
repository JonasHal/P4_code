import ndjson
import pandas as pd
from pathlib import Path


def extractProperties(filename):
    """

    :param filename: What file to open: for example Path("Data/universities_latest_all.ndjson")
    :return: returns a Python list with all the properties from the .ndjson file.
    """

    property_list = []

    with open(filename, encoding="utf-8") as f:
        wikidata = ndjson.load(f)

    wikidata_df = pd.DataFrame(wikidata)

    # Walks the .ndjson file and extracts the properties
    for i in range(len(wikidata_df)):
        property_list.append(list(wikidata_df["claims"][i].keys()))

    return property_list

def replacePcodesWithPlabels(nested_list):
    """

    :param nested_list: Input the nested list from the extractProperties function
    :return: new_list: A new list containing the same data as the original nested list only the
    P-codes are replaced with the P-label values from Wikidata.
    """
    # Converts the csv file containing P-codes and P label values to a dataframe
    property_label_dataframe = pd.read_csv(Path("Data/properties.csv"))
    property_label_dataframe.set_index(['Property'], inplace=True)

    new_list = []

    for list in nested_list:
        entity_list = []
        for prop in list:
            try:
                # if prop in property_label_dataframe.index:
                prop_label_value = property_label_dataframe.loc[prop,].Value
                entity_list.append(prop_label_value)
            except KeyError:
                print("The P-code does not exist in the property_label_dataframe")

        new_list.append(entity_list)

    return new_list


if __name__ == '__main__':
    property_list = extractProperties(Path("Data/universities_latest_all.ndjson"))
    property_list_with_labels = replacePcodesWithPlabels(property_list)
    print(property_list_with_labels)
