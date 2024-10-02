import json

file_path = r'F:\CodingEnvironment\tog\fci_graph.json'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
    data = json.load(file)

print(data)