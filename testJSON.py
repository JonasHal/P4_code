import json
import pandas as pd

testlist = []

with open("universities_latest_all.ndjson", encoding="utf-8") as f:
    for line in f:
        testlist.append(line)

#https://stackoverflow.com/questions/40588852/pandas-read-nested-json
df = pd.read_json('universities_latest_all.ndjson', lines=True)
#print(df['claims'])


