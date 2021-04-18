import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path

claims = pd.read_csv('q_claims.csv')
properties = pd.read_csv(Path('../../FaerdigKode/properties.csv'))
properties = properties.set_index(['Property'])
property_dict = properties.to_dict(orient='index')
for key in property_dict.keys():
    property_dict[key] = property_dict[key]['Value']

G = nx.DiGraph()
for i in range(len(claims)):
    G.add_edge(claims['subject'][i], claims['value'][i], label=claims['property'][i])
    print(round((100*i)/len(claims)), '% of edgy bois added')
pos = nx.spring_layout(G)
print('pos defined')
nx.draw_networkx(G)
print('nx.draw_networkx(G)')
nx.draw_networkx_edge_labels(G, pos=pos)
print('nx.draw_networkx_edge_labels(G, pos=pos)')
plt.show()
