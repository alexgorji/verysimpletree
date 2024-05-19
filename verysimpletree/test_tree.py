from unittest import TestCase

from verysimpletree.tree import Tree, ChildNotFoundError, grandchild1


class A(Tree):
    def __init__(self, name, parent=None, *args, **keyword):
        super().__init__(*args, **keyword)
        self._children = []
        self._parent = parent
        self.name = name

    def _check_child_to_be_added(self, child):
        if not isinstance(child, self.__class__):
            raise TypeError

    def add_child(self, name):
        child = type(self)(parent=self, name=name)
        return super().add_child(child)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class TestTree(TestCase):
    def setUp(self) -> None:
        self.root = A(name='root')
        self.child1 = self.root.add_child('child1')
        self.child2 = self.root.add_child('child2')
        self.child3 = self.root.add_child('child3')
        self.child4 = self.root.add_child('child4')
        self.grandchild1 = self.child2.add_child('grandchild1')
        self.grandchild2 = self.child2.add_child('grandchild2')
        self.grandchild3 = self.child4.add_child('grandchild3')
        self.greatgrandchild1 = self.grandchild2.add_child('greatgrandchild1')

    def test_is_last_child(self):
        t = self.root
        for node in t.traverse():
            if node.name in ['root', 'child4', 'grandchild2', 'grandchild3', 'greatgrandchild1']:
                assert node.is_last_child
            else:
                assert not node.is_last_child

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
        self.child1.add_child('grandchild')
        self.child1.add_child('grandchild')
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
