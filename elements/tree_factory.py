from elements.tree import Tree


class TreeFactory:
    def __init__(self):
        pass

    @staticmethod
    def get_tree(chain):
        prev = None
        curr = None
        for c in reversed(chain):
            curr = Tree(c)
            curr.add_child(prev)
            prev = curr
        return curr

    @staticmethod
    def connect_tree(forest, tree_b):
        if not forest:
            return [tree_b]

        for tree in forest:
            if tree.text == tree_b.text:
                tree.concat(tree_b)
                return forest
        forest.append(tree_b)
        return forest

    @staticmethod
    def set_root(root_name, forest):
        root = Tree(root_name)
        for tree in forest:
            root.add_child(tree)
        return root
