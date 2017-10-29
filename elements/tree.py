class Tree:
    def __init__(self, text):
        self.text = text
        self.children = list()
        self.contributors = set()

    def add_child(self, child):
        if not child or any(c.text == child.text for c in self.children):
            return
        self.children.append(child)

    def concat(self, other_tree):
        for other_c in other_tree.children:
            found = False
            for c in self.children:
                if c.text == other_c.text:
                    c.concat(other_c)
                    found = True
                    break
            if not found:
                self.children.append(other_c)

    def tree_to_dict(self):
        children = list()
        for c in self.children:
            children.append(c.tree_to_dict())
        return {"text": str(self.text), "children": children}
