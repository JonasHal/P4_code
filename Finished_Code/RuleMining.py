from mlxtend.frequent_patterns import fpgrowth, association_rules
from pathlib import Path
from extractPropertiesFromNDJSON import extractProperties
from PartitionData import splitBooleanDF
import pandas as pd
import time

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


def removeRulesWithId(rule_df):
    """
    Function used to remove properties of type ExternalId from consequents
    :param rule_df: The rules mined from the function association_rules() from mlxtend
    :return: The dataframe with the rules without properties of type ExternalId in consequents
    """
    property_label_dataframe = pd.read_csv(Path("../Data/properties.csv"))
    property_label_dataframe_externalIDs = property_label_dataframe[(property_label_dataframe["Type"] == "ExternalId")]
    property_label_dataframe_externalIDs.set_index(['Value'], inplace=True)
    list_of_ids = property_label_dataframe_externalIDs.index.tolist()

    # Changes the datatype of the consequents from frozenset, which is immutable, to a list.
    rule_df['consequents'] = [list(rule_df['consequents'][i]) for i in rule_df.index]

    amount_of_dropped_rules = 0

    for i in rule_df.index:
        if rule_df['consequents'][i][0] in list_of_ids:
            rule_df = rule_df.drop([i])
            amount_of_dropped_rules += 1

    print('A total amount of {} rules have been dropped from the inputted dataframe'.format(amount_of_dropped_rules))
    print('The amount of rules are now {0}'.format(len(rule_df)))

    unique_consequents = countUniqueConsequents(rule_df)
    print('The rules consist of {} unique consequents'.format(len(unique_consequents)))

    return rule_df


def countDuplicateRules(df1, df2):
    """
    counts duplicate rules in two partitions
    :param df1: a partition of the dataframe
    :param df2: another partition of the dataframe
    :return: the rules that appears in both partitions
    """
    test_df = pd.concat([df1, df2], ignore_index=True)
    result = sum(test_df.duplicated(keep=False))

    return result

def find_suggestions(rules, item):
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

    return suggestions

# The full list of properties
property_list = extractProperties(Path("../Data/universities_latest_all.ndjson"))

# upper_properties = splitBooleanDF(property_list, "upper")
middle_properties = splitBooleanDF(property_list, "middle")
# lower_properties = splitBooleanDF(property_list, "lower")

# frequent_items_lower = fpgrowth(lower_properties, min_support=0.0003, use_colnames=True)
frequent_items_middle = fpgrowth(middle_properties, min_support=0.006, use_colnames=True)

# upper_properties = splitBooleanDF(property_list, "upper")
middle_properties = splitBooleanDF(property_list, "middle")
# lower_properties = splitBooleanDF(property_list, "lower")

# frequent_items_lower = fpgrowth(lower_properties, min_support=0.0003, use_colnames=True)
frequent_items_middle = fpgrowth(middle_properties, min_support=0.006, use_colnames=True)

# lower_rules = association_rules(frequent_items_lower, metric="confidence", min_threshold=0.99)
# lower_rules["consequent_len"] = lower_rules["consequents"].apply(lambda x: len(x))
# lower_rules = lower_rules[(lower_rules['consequent_len'] == 1) & (lower_rules['lift'] > 1) &
#                            (lower_rules['leverage'] > 0)]

middle_rules = association_rules(frequent_items_middle, metric="confidence", min_threshold=0.99)
middle_rules["consequent_len"] = middle_rules["consequents"].apply(lambda x: len(x))
middle_rules = middle_rules[(middle_rules['consequent_len'] == 1) & (middle_rules['lift'] > 1) &
                            (middle_rules['leverage'] > 0)]

# lower_rules_without_id = removeRulesWithId(lower_rules)
# lower_rules_without_id = lower_rules_without_id.sort_values(by='leverage', ascending=False)

middle_rules_without_id = removeRulesWithId(middle_rules)
# middle_rules_without_id = middle_rules_without_id.sort_values(by='antecedents', key=lambda x: x.str.len())
middle_rules_without_id = middle_rules_without_id.sort_values(by='leverage', ascending=False)

test = ['street address', 'Integrated Postsecondary Education Data System ID',
        'Carnegie Classification of Institutions of Higher Education']

t1 = time.perf_counter()
ok = find_suggestions(middle_rules_without_id, test)
t2 = time.perf_counter()

print(t2 - t1)