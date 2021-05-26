import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
from pathlib import Path
from Finished_Code.extractPropertiesFromNDJSON import extractProperties

def replacePcodesWithPlabels(listofproperties, external_ids = True):
    """
    Replace P-values with P-labels
    :param listofproperties: Input the nested list from the extractProperties function
    :return: listofproperties_with_labels: A new list containing the same data as the original nested list
    only the P-codes are replaced with the P-label values from Wikidata.
    """
    # Converts the csv file containing P-codes and P label values to a dataframe
    property_label_dataframe = pd.read_csv(Path("../../Data/properties.csv"))
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

# property_list = extractProperties(Path("../../Data/universities_latest_all.ndjson"))
#
#

# property_list_labels = replacePcodesWithPlabels(property_list)
#
# te = TransactionEncoder()
# te_ary = te.fit(property_list_labels).transform(property_list_labels)
# df = pd.DataFrame(te_ary, columns=te.columns_)
#
# # FPgrowth algorithm:
#
# frequent_itemsets_growth = fpgrowth(df, min_support=0.08, use_colnames=True)
# # print(frequent_itemsets_growth.info())
# # print(frequent_itemsets_growth.describe())
# frequent_itemsets_growth["itemsets_len"] = frequent_itemsets_growth["itemsets"].apply(lambda x: len(x))
# frequent_itemsets_growth = frequent_itemsets_growth[
#     (frequent_itemsets_growth["itemsets_len"] >= 10)]
# frequent_itemsets_growth = frequent_itemsets_growth[['support', 'itemsets']]
#
# print(frequent_itemsets_growth.head(10))


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
frequent_itemsets_apriori = pd.read_csv(Path('../../Data/result1-1.txt'), sep=';')
frequent_itemsets_apriori.itemsets = [frequent_itemsets_apriori.itemsets[i].replace(' ', '').strip(')(').split(',') for i in range(len(frequent_itemsets_apriori))]
frequent_itemsets_apriori.itemsets = replacePcodesWithPlabels(frequent_itemsets_apriori.itemsets)
frequent_itemsets_apriori.itemsets = [frozenset(frequent_itemsets_apriori.itemsets[i]) for i in range(len(frequent_itemsets_apriori))]
#print(frequent_itemsets_apriori.tail())
association_rules_apriori = association_rules(frequent_itemsets_apriori, metric="confidence", min_threshold=0.7)
print(association_rules_apriori.head(10))

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

#results =
#print(results.tail())