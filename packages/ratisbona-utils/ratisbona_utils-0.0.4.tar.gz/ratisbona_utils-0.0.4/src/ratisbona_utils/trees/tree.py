from __future__ import annotations

from typing import Callable

import graphviz
from dataclasses import dataclass

@dataclass
class TreePathElem:
    name: str

    def __str__(self):
        return self.name
        #return f'<{self.name}>'

class TreePath:
    PATH_SEPARATOR='/'

    def __init__(self, *path_elems):
        self.path_elems = []
        for elem in path_elems:
            if isinstance(elem, TreePathElem):
                self.path_elems.append(elem)
            elif isinstance(elem, TreePath):
                self.path_elems.extend(elem.path_elems)
            else:
                self.path_elems.extend(TreePath.parse(elem).path_elems)

    @staticmethod
    def parse(path_string):
        raw_elems = path_string.split(TreePath.PATH_SEPARATOR)
        return TreePath(*[TreePathElem(elem) for elem in raw_elems if len(elem) > 0])

    def append(self, other):
        return TreePath(*self.path_elems, other)

    def __truediv__(self, other):
        return self.append(other)

    def __repr__(self):
        return TreePath.PATH_SEPARATOR + TreePath.PATH_SEPARATOR.join([str(elem) for elem in self.path_elems])


class Node:
    instance_count: int = 0

    def __init__(self, name: str):
        self.name = name
        self.id = Node.instance_count
        Node.instance_count += 1
        self.children: list[Node] = []

    def try_get_child(self, name: str):
        for child in self.children:
            if child.name == name:
                return child
        return None

    def ensure_child(self, name: str):
        maybe_child = self.try_get_child(name)
        if maybe_child is not None:
            return maybe_child
        new_node = Node(name)
        self.children.append(new_node)
        return new_node

    def visit_subtree(self, visitor: Callable[[Node], None]):
        visitor(self)
        for child in self.children:
            child.visit_subtree(visitor)


@dataclass
class TreeBuilder:
    root: Node = Node('<root>')

    def add_path(self, path: TreePath):
        next_node = self.root
        for elem in path.path_elems:
            next_node = next_node.ensure_child(elem.name)
        return next_node


class GraphVizitor:

    def __init__(self):
        self.dot = graphviz.Digraph()

    def __call__(self, node: Node):
        self.dot.node(str(node.id), node.name)
        for child in node.children:
            self.dot.edge(str(node.id), str(child.id))




    

