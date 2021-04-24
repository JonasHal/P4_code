import pandas as pd
from pathlib import Path
from FaerdigKode.extractPropertiesFromNDJSON import extractProperties
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpgrowth


def runtime_frequent(df, min_sup=0.5, frequent=True):
    import time

    fpgrowth_runtime = []
    apriori_runtime = []

    start_time = time.time()
    frequent_fp = fpgrowth(df, min_support=min_sup, use_colnames=True)
    fpgrowth_runtime.append(time.time() - start_time)

    start_time = time.time()
    frequent_apriori = apriori(df, min_support=min_sup, use_colnames=True)
    apriori_runtime.append(time.time() - start_time)

    df_runtime = pd.DataFrame(columns=["fpgrowth", "apriori"])

    df_runtime["fpgrowth"] = fpgrowth_runtime
    df_runtime["apriori"] = apriori_runtime

    if frequent == True:
        frequent_count = []
        frequent_count.append(len(frequent_fp))
        df_runtime["frequent_property_sets"] = frequent_count

    print(df_runtime)


if __name__ == "__main__":
    property_list = extractProperties(Path("../../Data/universities_latest_all.ndjson"))

    te = TransactionEncoder()
    te_ary = te.fit(property_list).transform(property_list)
    df = pd.DataFrame(te_ary, columns=te.columns_)

    print("the length of the dataframe is: " + str(len(df)))

    runtime_frequent(df, min_sup=0.2)
    runtime_frequent(df, min_sup=0.3)
    runtime_frequent(df, min_sup=0.4)
    runtime_frequent(df, min_sup=0.5)
    runtime_frequent(df, min_sup=0.6)
    runtime_frequent(df, min_sup=0.7)
    runtime_frequent(df, min_sup=0.8)

