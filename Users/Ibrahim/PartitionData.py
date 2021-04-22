from extractPropertiesFromNDJSON import extractProperties
from pathlib import Path
import pandas as pd
from Users.Magnus.PropertyDistUni import property_count_function, entity_property_count_function



if __name__ == '__main__':

    # The full list of properties
    property_list = extractProperties(Path("../../Data/universities_latest_all.ndjson"))

    # Uses the property_count_function to create a dataframe containing properties and their frequency.
    property_count_df = property_count_function(property_list)

    # Copy of the property_count_df that should be with P-codes and not P label values
    property_count_df_without_labels = property_count_df.copy()

    # Uses the function replacePcodesWithPlabels on the dataframe to make a new one with P label values
    property_count_df_with_labels = replacePcodesWithPlabels(property_count_df)

    fig = go.box(property_count_df_without_labels['Frequency'])
    fig.show()



    def getBoxplotValues():
        Q1 = df["COLUMN_NAME"].quantile(0.25)

        Q3 = df["COLUMN_NAME"].quantile(0.75)

        IQR = Q3 - Q1

        Lower_Fence = Q1 - (1.5 * IQR)

        Upper_Fence = Q3 + (1.5 * IQR)

        return Upper_Fence


above_trash = property_count_df_without_labels[property_count_df_without_labels['Frequency'] > getBoxplotValues()]
below_trash = property_count_df_without_labels[property_count_df_without_labels['Frequency'] <= getBoxplotValues()]



