import pandas as pd
from pathlib import Path
from Finished_Code.extractPropertiesFromNDJSON import extractProperties
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules
from Finished_Code.PartitionData import countUniqueConsequents, removeRulesWithId

property_list = extractProperties(Path("../Data/universities_latest_all.ndjson"))

te = TransactionEncoder()
te_ary = te.fit(property_list).transform(property_list)
boolean_dataframe = pd.DataFrame(te_ary, columns=te.columns_)
boolean_dataframe = boolean_dataframe.drop('P31', axis=1)

property_label_dataframe = pd.read_csv(Path("../Data/properties.csv"))

for prop in boolean_dataframe.columns:
    # This for loop goes trough each property and replaces it with each corresponding label
    if prop in list(property_label_dataframe['Property']):
        prop_label_value = property_label_dataframe.loc[property_label_dataframe['Property'] == prop,
                                                         'Value'].iloc[0]
        # # This line replaces the P-code with the P label value
        boolean_dataframe.rename({prop: prop_label_value}, axis='columns', inplace=True)

# apriori_fp = apriori(boolean_dataframe, min_support=0.2, use_colnames=True)
# apriori_fp = apriori_fp.sort_values(by=['support'], ascending=False)

fpgrowth_fp = fpgrowth(boolean_dataframe, min_support=0.2, use_colnames=True)
fpgrowth_fp = fpgrowth_fp.sort_values(by=['support'], ascending=False)

fpgrowth_rules = association_rules(fpgrowth_fp, metric="confidence", min_threshold=0.99)
fpgrowth_rules["consequent_len"] = fpgrowth_rules["consequents"].apply(lambda x: len(x))
fpgrowth_rules = fpgrowth_rules[(fpgrowth_rules['consequent_len'] == 1) & (fpgrowth_rules['lift'] > 1) &
                           (fpgrowth_rules['leverage'] > 0)]
fpgrowth_rules_without_id = removeRulesWithId(fpgrowth_rules)

print(countUniqueConsequents(fpgrowth_rules_without_id))

