from typing import List, Optional

from elements.element import Element

class NeighborFinder:
    def __init__(self, tree: List[Element]):
        self.tree=tree
        self.flat_list = self._flatten_tree(tree)
        self.index_map = {id(el): i for i, el in enumerate(self.flat_list)}

    def _flatten_tree(self, elements: List[Element]) -> List[Element]:
        result = []
        stack = elements[::-1]
        while stack:
            el = stack.pop()
            result.append(el)
            if hasattr(el, "children") and isinstance(el.children, list) and el.children:
                stack.extend(el.children[::-1])
        return result

    def get_before(self, target: Element) -> Optional[Element]:
        self.flat_list = self._flatten_tree(self.tree)
        self.index_map = {id(el): i for i, el in enumerate(self.flat_list)}
        idx = self.index_map.get(id(target))
        if idx is None or idx == 0:
            return None
        return self.flat_list[idx - 1]

    def get_after(self, target: Element) -> Optional[Element]:
        self.flat_list = self._flatten_tree(self.tree)
        self.index_map = {id(el): i for i, el in enumerate(self.flat_list)}
        idx = self.index_map.get(id(target))
        if idx is None or idx == len(self.flat_list) - 1:
            return None
        return self.flat_list[idx + 1]
