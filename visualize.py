import pyvis
def visualize_graph(graph_chunks):
    graph = pyvis.network.Network(width="100%")
    for graph_chunk in graph_chunks:
        for node in graph_chunk['nodes']:
            graph.add_node(node['name'], node['name'], group=node['type'])
        for relationship in graph_chunk['relationships']:
            graph.add_edge(relationship['source']['name'], relationship['target']['name'], title=relationship['type'])
    graph.show_buttons()
    graph.toggle_physics(True)
    graph.show('graph.html', notebook=False)

import json

file_path = r'F:\CodingEnvironment\tog\graph.json'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
    data = json.load(file)

visualize_graph(data)