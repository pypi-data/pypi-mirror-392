from unittest import TestCase
from ratisbona_utils.trees import TreePath, TreePathElem, TreeBuilder, GraphVizitor


class TreeTest(TestCase):
    def test_creating_treepath_must_result_in_empty_path(self):
        path = TreePath()
        self.assertEqual(str(path), "/")
        self.assertEqual(path.path_elems, [])

    def test_creating_treepath_by_parsing_single_element_must_result_in_root_with_one_subelement(
        self,
    ):
        path = TreePath.parse("home")
        self.assertEqual(str(path), "/home")
        self.assertEqual(path.path_elems, [TreePathElem("home")])

    def test_parsing_path_with_multiple_elements_must_result_in_correct_path(self):
        path = TreePath.parse("home/kevin")
        self.assertEqual(str(path), "/home/kevin")
        self.assertEqual(path.path_elems, [TreePathElem("home"), TreePathElem("kevin")])

    def test_creating_path_from_string_must_result_in_correct_path(self):
        path = TreePath("home")
        self.assertEqual(str(path), "/home")
        self.assertEqual(path.path_elems, [TreePathElem("home")])

    def test_appending_path_to_path_must_result_in_correct_path(self):
        path = TreePath() / "home" / "kevin"
        self.assertEqual(str(path), "/home/kevin")
        self.assertEqual(path.path_elems, [TreePathElem("home"), TreePathElem("kevin")])

    def test_appending_path_by_division_operator_must_result_in_correct_path(self):
        path = TreePath("/") / "home" / "kevin"
        self.assertEqual(str(path), "/home/kevin")
        self.assertEqual(path.path_elems, [TreePathElem("home"), TreePathElem("kevin")])

    def build_testtree(self):
        builder = TreeBuilder()
        builder.add_path(TreePath("/home/kevin/Documents"))
        builder.add_path(TreePath() / "usr" / "share" / "uae")
        builder.add_path(TreePath("/home/kevin/opt/amiga/uae.info"))
        return builder.root

    def test_treebuilder(self):
        root_node = self.build_testtree()
        self.assertEqual(root_node.name, "<root>")
        self.assertEqual(len(root_node.children), 2)
        home_node = root_node.children[0]
        self.assertEqual(home_node.name, "home")
        self.assertEqual(len(home_node.children), 1)
        kevin_node = home_node.children[0]
        self.assertEqual(kevin_node.name, "kevin")
        self.assertEqual(len(kevin_node.children), 2)
        documents_node = kevin_node.children[0]
        self.assertEqual(documents_node.name, "Documents")
        self.assertEqual(len(documents_node.children), 0)
        opt_node = kevin_node.children[1]
        self.assertEqual(opt_node.name, "opt")
        self.assertEqual(len(opt_node.children), 1)
        amiga_node = opt_node.children[0]
        self.assertEqual(amiga_node.name, "amiga")
        self.assertEqual(len(amiga_node.children), 1)
        uae_node = amiga_node.children[0]
        self.assertEqual(uae_node.name, "uae.info")
        self.assertEqual(len(uae_node.children), 0)
        usr_node = root_node.children[1]
        self.assertEqual(usr_node.name, "usr")
        self.assertEqual(len(usr_node.children), 1)
        share_node = usr_node.children[0]
        self.assertEqual(share_node.name, "share")
        self.assertEqual(len(share_node.children), 1)
        uae_node = share_node.children[0]
        self.assertEqual(uae_node.name, "uae")
        self.assertEqual(len(uae_node.children), 0)

    def test_graphvizitor_must_yield_tree_as_dot(self):
        root_node = self.build_testtree()

        graphvizitor = GraphVizitor()
        root_node.visit_subtree(graphvizitor)

        print(graphvizitor.dot)
        # assert that it is
        self.assertEqual(
            str(graphvizitor.dot).strip(),
            """digraph {
	0 [label=<root>]
	0 -> 1
	0 -> 4
	1 [label=home]
	1 -> 2
	2 [label=kevin]
	2 -> 3
	2 -> 7
	3 [label=Documents]
	7 [label=opt]
	7 -> 8
	8 [label=amiga]
	8 -> 9
	9 [label="uae.info"]
	4 [label=usr]
	4 -> 5
	5 [label=share]
	5 -> 6
	6 [label=uae]
}""".strip())
        # graphvizitor.dot.render('test_graph.gv', format='jpg',view=True)

