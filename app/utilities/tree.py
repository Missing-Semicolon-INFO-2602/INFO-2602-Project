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


def build_tree(animals):
    root = {"name": "Life", "children": []}
    for a in animals:
        insert_path(root, [a.kingdom, a.phylum, a.class_, a.order, a.family, a.species])
    return root
