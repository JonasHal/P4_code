import ndjson
import pandas as pd
from pathlib import Path
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpgrowth

from extractPropertiesFromNDJSON import extractProperties

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

property_list = extractProperties(Path("../../Data/universities_latest_all.ndjson"))

property_list_name = replacePcodesWithPlabels(property_list)

te = TransactionEncoder()
te_ary = te.fit(property_list_name).transform(property_list_name)
df = pd.DataFrame(te_ary, columns=te.columns_)

frequent_itemsets_growth = fpgrowth(df, min_support=0.5, use_colnames=True)
frequent_itemsets_apriori = apriori(df, min_support=0.5, use_colnames=True)

frequent_itemsets_growth.to_csv("growth.csv")
frequent_itemsets_apriori.to_csv("apriori.csv")
