import json

def insert_path(root, path):
    current = root
    for level in path:
        found = next((c for c in current["children"] if c["name"] == level), None)
        if not found:
            new_node = {"name": level, "children": []}
            current["children"].append(new_node)
            current = new_node
        else:
            current = found

tree = {"name": "Life", "children": []}

for animal in animals:
    path = [
        animal["kingdom"],
        animal["phylum"],
        animal["class"],
        animal["order"],
        animal["family"],
        animal["genus"],
        animal["species"]
    ]
    insert_path(tree, path)

with open("animals_tree.json", "w") as f:
    json.dump(tree, f, indent=2)