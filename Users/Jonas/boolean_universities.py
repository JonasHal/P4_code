import pandas as pd
from extractPropertiesFromNDJSON import extractProperties, extractItemCodes
from pathlib import Path
from mlxtend.preprocessing import TransactionEncoder

property_list = extractProperties(Path("../../Data/universities_latest_all.ndjson"))
item_list = extractItemCodes(Path("../../Data/universities_latest_all.ndjson"))

te = TransactionEncoder()
te_ary = te.fit(property_list).transform(property_list)
property_dataframe = pd.DataFrame(te_ary, columns=te.columns_, index=item_list)

property_label_dataframe = pd.read_csv(Path("../../Data/properties.csv"))

print(property_dataframe[["P17", "P580", "P463", "P373"]].head(5))