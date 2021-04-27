import pandas as pd
from pathlib import Path
from FaerdigKode.extractPropertiesFromNDJSON import extractProperties
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpgrowth, association_rules
from aifc import Error


property_list = extractProperties(Path("../Data/universities_latest_all.ndjson"))

te = TransactionEncoder()
te_ary = te.fit(property_list).transform(property_list)
property_dataframe = pd.DataFrame(te_ary, columns=te.columns_)
property_dataframe = property_dataframe.drop('P31', axis=1)

property_label_dataframe = pd.read_csv(Path("../Data/properties.csv"))

for prop in property_dataframe.columns:
    # This for loop goes trough each property and replaces it with each corresponding label
    if prop in list(property_label_dataframe['Property']):
        prop_label_value = property_label_dataframe.loc[property_label_dataframe['Property'] == prop,
                                                         'Value'].iloc[0]
        # # This line replaces the P-code with the P label value
        property_dataframe.rename({prop: prop_label_value}, axis='columns', inplace=True)

def runAlgorthims(property_dataframe, type, minSub):
    apriori_frequent_properties = apriori(property_dataframe, min_support=minSub, use_colnames=True)
    fpgrowth_frequent_properties = fpgrowth(property_dataframe, min_support=minSub, use_colnames=True)

    if type == 'apriori':
        return apriori_frequent_properties
    elif type == 'fpgrowth':
        return fpgrowth_frequent_properties
    else:
        raise Error("Please enter apriori or fpgrowth")

#property_rules = association_rules(runAlgorthims(property_dataframe, 'apriori'), metric="lift", min_threshold=1.1)