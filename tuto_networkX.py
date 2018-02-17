import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()
G.add_node(1, label='1')
G.add_node(2, label='2')
G.add_node(3, label='3')
G.add_edge(1,2,label="X < 3")

pos = nx.spring_layout(G)

nx.draw(G, pos, with_labels = True, font_weight='bold')
node_labels = nx.get_node_attributes(G,'label')
nx.draw_networkx_labels(G, pos, labels = node_labels)
edge_labels = nx.get_edge_attributes(G,'label')
nx.draw_networkx_edge_labels(G, pos, labels = edge_labels)
plt.show()
