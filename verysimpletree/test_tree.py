from typing import Any
from unittest import TestCase

from verysimpletree.tree import Tree, ChildNotFoundError, grandchild1, TreeReferenceError


class AContent:
    def __init__(self, value):
        self.value = value


class BContent:
    def __init__(self, value):
        self.value = value


class A(Tree[Any]):
    def __init__(self, name, parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._children = []
        self._parent = parent
        self.name = name
        self.content = AContent(value=10)

    def _check_child_to_be_added(self, child):
        if not isinstance(child, Tree):
            raise TypeError

    def add_child_by_name(self, name):
        child = self.__class__(parent=self, name=name)
        return super().add_child(child)

    def __str__(self):
        return self.name


class B(Tree[Any]):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.content = BContent(value=10)

    def _check_child_to_be_added(self, child):  # pragma: no cover
        if not isinstance(child, Tree):
            raise TypeError

class C(Tree[Any]):
    def __init__(self, name, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.value = value

    def _check_child_to_be_added(self, child):  # pragma: no cover
        if not isinstance(child, Tree):
            raise TypeError

class TreeTestCase(TestCase):
    def setUp(self) -> None:
        self.root = A(name='root')
        self.child1 = self.root.add_child_by_name('child1')
        self.child2 = self.root.add_child_by_name('child2')
        self.child3 = self.root.add_child_by_name('child3')
        self.child4 = self.root.add_child_by_name('child4')
        self.grandchild1 = self.child2.add_child_by_name('grandchild1')
        self.grandchild2 = self.child2.add_child_by_name('grandchild2')
        self.grandchild3 = self.child4.add_child_by_name('grandchild3')
        self.greatgrandchild1 = self.grandchild2.add_child_by_name('greatgrandchild1')

class Test(TreeTestCase):
    def test_is_last_child(self):
        t = self.root
        for node in t.traverse():
            if node.name in ['root', 'child4', 'grandchild2', 'grandchild3', 'greatgrandchild1']:
                assert node.is_last_child
            else:
                assert not node.is_last_child

    def test_is_first_child(self):
        t = self.root
        for node in t.traverse():
            if node.name in ['root', 'child1', 'grandchild1', 'grandchild3', 'greatgrandchild1']:
                assert node.is_first_child
            else:
                assert not node.is_first_child

    def test_get_root(self):
        assert self.greatgrandchild1.get_root() == self.root
        assert self.child4.get_root() == self.root
        assert self.root.get_root() == self.root

    def test_is_leaf(self):
        assert self.greatgrandchild1.is_leaf is True
        assert self.child4.is_leaf is False
        assert self.child3.is_leaf is True

    def test_traverse(self):
        assert list(self.root.traverse()) == [self.root, self.child1, self.child2, self.grandchild1, self.grandchild2,
                                              self.greatgrandchild1, self.child3, self.child4, self.grandchild3]

    def test_iterate_leaves(self):
        assert list(self.root.iterate_leaves()) == [self.child1, self.grandchild1, self.greatgrandchild1,
                                                    self.child3, self.grandchild3]

    def test_level(self):
        assert [node.get_level() for node in self.root.traverse()] == [0, 1, 1, 2, 2, 3, 1, 1, 2]
        assert self.greatgrandchild1.get_level() == 3
        assert self.grandchild2.get_level() == 2
        assert self.child4.get_level() == 1
        assert self.root.get_level() == 0

    def test_reversed_path_to_root(self):
        assert list(self.greatgrandchild1.get_reversed_path_to_root()) == [self.greatgrandchild1, self.grandchild2,
                                                                           self.child2, self.root]

    def test_remove_child(self):
        with self.assertRaises(ChildNotFoundError):
            self.child2.remove(self.child1)

        self.child2.remove(self.grandchild2)
        assert self.child2.get_children() == [self.grandchild1]
        assert self.grandchild2.get_parent() is None
        assert self.greatgrandchild1.get_parent() == self.grandchild2

    def test_get_coordinates(self):
        assert self.greatgrandchild1.get_position_in_tree() == '2.2.1'
        assert self.child2.get_position_in_tree() == '2'
        assert self.root.get_position_in_tree() == '0'

    def test_replace_child(self):
        self.child2.replace_child(self.grandchild1, A(name='new_grand_child'))
        assert [ch.name for ch in self.child2.get_children()] == ['new_grand_child', 'grandchild2']
        self.child1.add_child_by_name('grandchild')
        self.child1.add_child_by_name('grandchild')
        new = A(name='other_new_grand_child')
        self.child1.replace_child(lambda x: x.name == 'grandchild', new, 1)
        assert new.get_parent() == self.child1
        assert [ch.name for ch in self.child1.get_children()] == ['grandchild', 'other_new_grand_child']
        with self.assertRaises(ValueError):
            self.child2.replace_child(None, None)
        with self.assertRaises(TypeError):
            self.root.replace_child(self.child1, 34)

    def test_previous(self):
        assert self.child4.previous == self.child3
        assert self.child3.previous == self.child2
        assert self.child2.previous == self.child1
        assert self.child1.previous is None

    def test_next(self):
        assert self.child1.next == self.child2
        assert self.child2.next == self.child3
        assert self.child3.next == self.child4
        assert self.child4.next is None

    def test_get_leaves(self):
        assert self.root.get_leaves(key=lambda x: x.name) == ['child1', ['grandchild1', ['greatgrandchild1']], 'child3',
                                                              ['grandchild3']]

    def test_get_layer(self):
        assert self.root.get_layer(0) == [self.root]
        assert self.root.get_layer(1) == [self.child1, self.child2, self.child3, self.child4]
        assert self.root.get_layer(2) == [self.child1, self.grandchild1, self.grandchild2, self.child3,
                                          self.grandchild3]
        assert self.root.get_layer(3) == [self.child1, self.grandchild1, self.greatgrandchild1, self.child3,
                                          self.grandchild3]
        assert self.root.get_layer(4) == [self.child1, self.grandchild1, self.greatgrandchild1, self.child3,
                                          self.grandchild3]

    def test_get_farthest_leaf(self):
        pass

    def test_find_grandchild(self):
        assert [n for n in self.root.traverse() if n.get_level() == 2] == [self.grandchild1, self.grandchild2,
                                                                           self.grandchild3]
        for n in self.root.traverse():
            if n.get_level() == 2:
                print(n)
                break

    def test_content(self):
        self.child1.content.value = 20
        assert [ch.content.value for ch in self.root.get_children()] == [20, 10, 10, 10]

    def test_get_wrong_distance(self):
        with self.assertRaises(TreeReferenceError):
            assert self.greatgrandchild1.get_distance(self.child1) == 'bla'

    def test_get_farthest_leave_of_root_without_children(self):
        root = A('root')
        assert root.get_farthest_leaf() == root

    def test_get_leaves_of_root_without_children(self):
        root = A('root')
        assert root.get_leaves() == [root]
        assert root.get_leaves(key=lambda node: node.name) == ['root']

    def test_get_number_of_layers_of_root_without_children(self):
        root = A('root')
        assert root.get_number_of_layers() == 0

    def test_get_layer_with_key(self):
        assert self.root.get_layer(1, lambda node: node.name) == ['child1', 'child2', 'child3', 'child4']
        assert self.root.get_layer(2, lambda node: node.name) == ['child1', 'grandchild1', 'grandchild2', 'child3',
                                                                  'grandchild3']
        assert self.root.get_layer(3, lambda node: node.name) == ['child1', 'grandchild1', 'greatgrandchild1', 'child3',
                                                                  'grandchild3']

    def test_remove_children(self):
        self.root.remove_children()
        assert self.root.get_children() == []
        assert self.child1.name == 'child1'

    def test_tree_representation_wrong_space(self):
        with self.assertRaises(TypeError):
            self.root.get_tree_representation(space=None)
        with self.assertRaises(ValueError):
            self.root.get_tree_representation(space=0)

    def test_get_tree_representation(self):
        expected = """└── root
    ├── child1
    ├── child2
    │   ├── grandchild1
    │   └── grandchild2
    │       └── greatgrandchild1
    ├── child3
    └── child4
        └── grandchild3
"""

        assert self.root.get_tree_representation() == expected


class TreeListRepresentationTestCase(TreeTestCase):

    def test_get_list_representation_all(self):
        assert self.root.get_list_representation(key=lambda node: node.name) == ['root', ['child1'], ['child2', ['grandchild1'], ['grandchild2', ['greatgrandchild1']]], ['child3'], ['child4', ['grandchild3']]]

    def test_get_list_representation_only_root(self):
        a = A(name='root')
        assert a.get_list_representation(key=lambda node: node.name) == ['root']

    def test_create_tree_from_list(self):
        tree = A.create_tree_from_list(self.root.get_list_representation(key=lambda node: node.name), 'name')
        assert tree.get_list_representation(key=lambda node: node.name) == self.root.get_list_representation(key=lambda node: node.name)

    def test_create_tree_from_list_only_root(self):
        tree = A.create_tree_from_list(self.root.get_list_representation(key=lambda node: node.name), 'name')
        assert tree.get_list_representation(key=lambda node: node.name) == self.root.get_list_representation(key=lambda node: node.name)

    def test_create_tree_from_list_with_name_and_value(self):
        def _copy_node(node, current_value):
            copied = C(name=node.name, value=current_value)
            current_value += 1
            for child in node.get_children():
                copied.add_child(_copy_node(child, current_value=current_value))
            return copied
        
        copied_c = _copy_node(self.root, 0)
        representation = copied_c.get_list_representation(key=lambda node: [node.name, node.value])
        assert representation == [['root', 0], [['child1', 1]], [['child2', 1], [['grandchild1', 2]], [['grandchild2', 2], [['greatgrandchild1', 3]]]], [['child3', 1]], [['child4', 1], [['grandchild3', 2]]]]
        tree = C.create_tree_from_list(representation, ['name', 'value'])
        assert tree.get_list_representation(key=lambda node: [node.name, node.value]) == copied_c.get_list_representation(key=lambda node: [node.name, node.value])


class TestNodeReturnValue(TestCase):

    def test_with_string(self):
        assert grandchild1.get_self_with_key(key='name') == 'grandchild1'
        with self.assertRaises(AttributeError):
            grandchild1.get_self_with_key(key='wrong')

    def test_with_callable(self):
        assert grandchild1.get_self_with_key(key=lambda node: node.get_position_in_tree()) == '2.1'
        with self.assertRaises(AttributeError):
            grandchild1.get_self_with_key(key=lambda node: node.wrong_method())

    def test_with_node(self):
        assert grandchild1.get_self_with_key() == grandchild1.get_self_with_key(key=None) == grandchild1

    def test_wrong_type(self):
        with self.assertRaises(TypeError):
            grandchild1.get_self_with_key(key=1)


class TestTwoTypesOfChildren(TestCase):
    def setUp(self) -> None:
        self.root = A(name='root_a')
        self.ach1 = self.root.add_child(A(name='b_child_1'))
        self.bch1 = self.root.add_child(B(name='a_child_1'))
        self.ach2 = self.root.add_child(A(name='b_child_2'))
        self.bch2 = self.root.add_child(B(name='a_child_2'))

    def test_get_children_of_type(self):
        assert self.root.get_children() == [self.ach1, self.bch1, self.ach2, self.bch2]
        assert self.root.get_children_of_type(A) == [self.ach1, self.ach2]
        assert self.root.get_children_of_type(B) == [self.bch1, self.bch2]
