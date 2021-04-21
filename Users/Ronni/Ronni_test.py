import ndjson
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpmax, fpgrowth
from mlxtend.frequent_patterns import association_rules
from pathlib import Path
from extractPropertiesFromNDJSON import extractProperties

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

te = TransactionEncoder()
te_ary = te.fit(property_list_labels).transform(property_list_labels)
df = pd.DataFrame(te_ary, columns=te.columns_)

# FPgrowth algorithm:

frequent_itemsets_growth = fpgrowth(df, min_support=0.5, use_colnames=True)
# print(frequent_itemsets_growth.info())
# print(frequent_itemsets_growth.describe())
frequent_itemsets_growth["itemsets_len"] = frequent_itemsets_growth["itemsets"].apply(lambda x: len(x))
frequent_itemsets_growth = frequent_itemsets_growth[
    (frequent_itemsets_growth["itemsets_len"] >= 5)]
frequent_itemsets_growth = frequent_itemsets_growth[['support', 'itemsets']]

print(frequent_itemsets_growth.head(10))


# association_rules_growth = association_rules(frequent_itemsets_growth, metric="confidence", min_threshold=0.7)
# print(association_rules.info())
# print(association_rules_growth.head(10))

# rules_growth = association_rules(frequent_itemsets_growth, metric="lift", min_threshold=1.2)
# rules_growth["antecedent_len"] = rules_growth["antecedents"].apply(lambda x: len(x))
# rules_growth = rules_growth[
#     (rules_growth["antecedent_len"] >= 5) &
#     (rules_growth["confidence"] > 0.75) &
#     (rules_growth["lift"] > 1.2)]
# rules_growth = rules_growth[['antecedents', 'consequents', 'support', 'confidence', 'lift']]
# print(rules_growth.head(10))

# Apriori algorithm:
# frequent_itemsets_apriori = apriori(df, min_support=0.5, use_colnames=True)
# association_rules_apriori = association_rules(frequent_itemsets_apriori, metric="confidence", min_threshold=0.7)
# # print(association_rules_apriori.head(10))
#
# rules_apriori = association_rules(frequent_itemsets_apriori, metric="lift", min_threshold=1.2)
# rules_apriori["antecedent_len"] = rules_apriori["antecedents"].apply(lambda x: len(x))
# rules_apriori = rules_apriori[
#     (rules_apriori["antecedent_len"] >= 2) &
#     (rules_apriori["confidence"] > 0.75) &
#     (rules_apriori["lift"] > 1.2)]
# rules_apriori = rules_apriori[['antecedents', 'consequents', 'support', 'confidence', 'lift', 'leverage']]
# print(rules_apriori.head(25))

# FPmax algorithm:
# frequent_itemsets_max = fpmax(df, min_support=0.6, use_colnames=True)
# association_rules_max = association_rules(frequent_itemsets_max, metric="confidence", min_threshold=0.7)
# print(association_rules_max.head(10))

# Sammenligning mellem to hyppige itemsets
# compared = frequent_itemsets_growth.compare(frequent_itemsets_apriori, keep_equal=True)
# print(compared.head(10))
