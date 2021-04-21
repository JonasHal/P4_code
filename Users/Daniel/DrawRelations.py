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
for i in range(0, 100, 5):
    G.add_edge(claims['subject'][i], claims['value'][i], label=claims['property'][i])
#pos = nx.spring_layout(G)
pos = nx.spring_layout(G)
edge_labels = nx.get_edge_attributes(G, 'label')
#nx.draw_networkx(G, pos=pos)
nx.draw_networkx_nodes(G, pos, node_size=14)
nx.draw_networkx_edges(G, pos, arrowsize=10)
nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=7)
nx.draw_networkx_labels(G, pos, font_size=7)
plt.tight_layout()
plt.show()

#print(G.edges)