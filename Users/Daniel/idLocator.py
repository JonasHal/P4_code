import pandas as pd
from pathlib import Path
from FaerdigKode.extractPropertiesFromNDJSON import extractProperties

property_list = extractProperties(Path("../../Data/universities_latest_all.ndjson"))


def replacePcodesWithPlabels(df):
    # Converts the csv file containing P-codes and P label values to a dataframe
    property_label_dataframe = pd.read_csv(Path("../../Data/properties.csv"))

    df_name = []

    for list in df:
        entity_list = []
        for prop in list:
            if prop in set(property_label_dataframe['Property']):
                prop_label_value = property_label_dataframe.loc[property_label_dataframe['Property'] == prop,
                                                                'Value'].iloc[0]
                entity_list.append(prop_label_value)
        df_name.append(entity_list)

    return df_name


property_list_labels = replacePcodesWithPlabels(property_list)

print(property_list_labels)
