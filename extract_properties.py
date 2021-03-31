import ndjson
import pandas as pd


filename = "universities_latest_all.ndjson"
property_list = []

#Open and read the file to a value
with open(filename, encoding="utf-8") as f:
    data = ndjson.load(f)

df = pd.DataFrame(data)

#Walks .ndjson file and extracts the properties
for i in range(len(df)):
    property_list.append(list(df["claims"][i].keys()))

print(property_list)