import ndjson
import pandas as pd
from pathlib import Path
from extractPropertiesFromNDJSON import extractProperties
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, fpmax, fpgrowth
from mlxtend.frequent_patterns import association_rules

def runtime_frequent(df, min_sup=0.5):
    import time

    fpgrowth_runtime = []
    apriori_runtime = []


    start_time = time.time()
    fpgrowth(df, min_support=min_sup, use_colnames=True)
    fpgrowth_runtime.append(time.time() - start_time)


    start_time = time.time()
    apriori(df, min_support=min_sup, use_colnames=True)
    apriori_runtime.append(time.time() - start_time)

    df_runtime = pd.DataFrame(columns=["fpgrowth", "apriori"])

    df_runtime["fpgrowth"] = fpgrowth_runtime
    df_runtime["apriori"] = apriori_runtime

    print(df_runtime)


if __name__ == "__main__":
    # filename = "..\\..\\Data\\universities_latest_all.ndjson"
    # property_list = []
    #
    # # Open and read the file to a value
    # with open(filename, encoding="utf-8") as f:
    #     data = ndjson.load(f)
    #
    # df = pd.DataFrame(data)
    #
    # # Walks .ndjson file and extracts the properties
    # for i in range(len(df)):
    #     property_list.append(list(df["claims"][i].keys()))

    property_list = extractProperties(Path("../../Data/universities_latest_all.ndjson"))

    te = TransactionEncoder()
    te_ary = te.fit(property_list).transform(property_list)
    df = pd.DataFrame(te_ary, columns=te.columns_)

    runtime_frequent(df, min_sup=0.2)
    # runtime_frequent(df, min_sup=0.3)
    # runtime_frequent(df, min_sup=0.4)
    # runtime_frequent(df, min_sup=0.5)
    # runtime_frequent(df, min_sup=0.6)
    # runtime_frequent(df, min_sup=0.7)
    # runtime_frequent(df, min_sup=0.8)

