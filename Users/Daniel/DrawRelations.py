import ndjson
import pandas as pd
from pathlib import Path

with open(Path('../../Data/universities_latest_all.ndjson'), encoding="utf-8") as f:
    wikidata = ndjson.load(f)
    wikidata_df = pd.DataFrame(wikidata)
    df2 = wikidata_df[['id', 'labels', 'claims']]
    for i in range(len(df2)):
        try:
            df2['labels'][i] = df2['labels'][i]['en']
        except KeyError:
            df2['labels'][i] = 'NO ENGLISH LABEL FOUND'

df3 = pd.DataFrame(columns=['subject', 'property', 'value'])

for row in range(len(df2)):
    if row % 50 == 0:
        print(row, len(df2) - row, 'rows remaining')
    #for key in df2['claims'][row].keys():
    #    if df2['claims'][row][key][0]['mainsnak']['snaktype'] != 'value':
    #        df3 = df3.append({'subject': df2['id'][row], 'property': key, 'value': df2['claims'][row][key][0]['mainsnak']['snaktype']}, ignore_index=True)
    #    elif isinstance(df2['claims'][row][key][0]['mainsnak']['datavalue']['value'], dict):
    #        df3 = df3.append({'subject': df2['id'][row], 'property': key, 'value': df2['claims'][row][key][0]['mainsnak']['datavalue']['value']}, ignore_index=True)
    #    else:
    #        df3 = df3.append({'subject': df2['id'][row], 'property': key, 'value': df2['claims'][row][key][0]['mainsnak']['datavalue']['value']}, ignore_index=True)

    for key in df2['claims'][row].keys():
        if df2['claims'][row][key][0]['mainsnak']['snaktype'] == 'value':
            if isinstance(df2['claims'][row][key][0]['mainsnak']['datavalue']['value'], dict):
                if 'id' in df2['claims'][row][key][0]['mainsnak']['datavalue']['value'].keys():
                    df3 = df3.append({'subject': df2['id'][row], 'property': key, 'value': df2['claims'][row][key][0]['mainsnak']['datavalue']['value']['id']}, ignore_index=True)
                else:
                    df3 = df3.append({'subject': df2['id'][row], 'property': key, 'value': df2['claims'][row][key][0]['mainsnak']['datavalue']['value']}, ignore_index=True)

            else:
                df3 = df3.append({'subject': df2['id'][row], 'property': key, 'value': df2['claims'][row][key][0]['mainsnak']['datavalue']['value']}, ignore_index=True)

print(df3.head())
df3.to_csv('useful_claims.csv', index = False)
# TODO: Få udpakket dictionaries pba. property-typen