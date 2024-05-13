from abc import ABC, abstractmethod
from typing import Optional, Callable, List, Iterator, Union


class TreeException(Exception):
    pass


class ChildNotFoundError(TreeException):
    pass


class Tree(ABC):
    """
    An abstract lightweight tree class for managing tree structures in MusicXML and musicscore packages.
    """
    _TREE_ATTRIBUTES = {'compact_repr', 'is_leaf', 'is_last_child', 'is_root', '_parent', '_children',
                        'up'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._parent = None
        self._children = []
        self._traversed = None
        self._is_leaf = True
        self._iterated_leaves = None
        self._reversed_path_to_root = None

    @abstractmethod
    def _check_child_to_be_added(self, child):
        pass

    def _raw_traverse(self):
        yield self
        for child in self.get_children():
            for node in child._raw_traverse():
                yield node

    def _raw_reversed_path_to_root(self):
        yield self
        if self.get_parent():
            for node in self.get_parent().get_reversed_path_to_root():
                yield node

    def _reset_iterators(self):
        """
        This method is used to reset both parent's and this class's iterators for :obj:'~traverse', obj:'~iterate_leaves' and obj:'~get_reversed_path_to_root'
        """
        if self.up:
            self.up._reset_iterators()
        self._traversed = None
        self._iterated_leaves = None
        self._reversed_path_to_root = None

    @property
    def compact_repr(self) -> str:
        """
        :obj:`~tree.tree.Tree` property

        :return: compact representation of a node. Default is the string representation. This property is used as default in the :obj:`~tree_representation` method and can be
                 customized in subclasses to get the most appropriate representation.
        :rtype: str
        """
        return self.__str__()

    @property
    def is_last_child(self):
        """
        >>> t = TestTree('root')
        >>> for node in t.traverse():
        ...    if node.name in ['root', 'child4', 'grandchild2', 'grandchild3', 'greatgrandchild1']:
        ...        assert node.is_last_child
        ...    else:
        ...        assert not node.is_last_child
        """
        if self.is_root:
            return True
        if self.up.get_children()[-1] == self:
            return True
        return False

    @property
    def is_leaf(self) -> bool:
        """
        :obj:`~tree.tree.Tree` property

        :return: ``True`` if self has no children. ``False`` if self has one or more children.
        :rtype: bool
        """
        return self._is_leaf

    @property
    def is_root(self) -> bool:
        """
        :obj:`~tree.tree.Tree` property

        :return: ``True`` if self has no parent, else ``False``.
        :rtype: bool
        """
        return True if self.get_parent() is None else False

    def get_level(self) -> int:
        """
        :obj:`~tree.tree.Tree`

        :return: ``0`` for ``root``, ``1, 2 etc.`` for each layer of children
        :rtype: nonnegative int

        >>> class TestTree(Tree):
        ...   def _check_child_to_be_added(self, child):
        ...      return True
        >>> root = TestTree()
        >>> root.get_level()
        0
        >>> ch = root.add_child(TestTree()).add_child(TestTree()).add_child(TestTree())
        >>> ch.get_level()
        3
        """
        if self.get_parent() is None:
            return 0
        else:
            return self.get_parent().get_level() + 1

    @property
    def next(self) -> Optional['Tree']:
        """
        :obj:`~tree.tree.Tree` property

        :return: next sibling. ``None`` if this is the last current child of the parent.
        :rtype: :obj:`~tree.tree.Tree`
        """
        if self.up and self != self.up.get_children()[-1]:
            return self.up.get_children()[self.up.get_children().index(self) + 1]
        else:
            return None

    @property
    def previous(self) -> Optional['Tree']:
        """
        :obj:`~tree.tree.Tree` property

        :return: previous sibling. ``None`` if this is the first child of the parent.
        :rtype: :obj:`~tree.tree.Tree`
        """
        if self.up and self != self.up.get_children()[0]:
            return self.up.get_children()[self.up.get_children().index(self) - 1]
        else:
            return None

    @property
    def up(self) -> 'Tree':
        """
        :obj:`~tree.tree.Tree` property

        :return: :obj:`get_parent()`
        :rtype: :obj:`~tree.tree.Tree`
        """
        return self.get_parent()

    def add_child(self, child: 'Tree') -> 'Tree':
        """
        :obj:`~tree.tree.Tree` method

        Check and add child to list of children. Child's parent is set to self.

        :param child:
        :return: child
        :rtype: :obj:`~tree.tree.Tree`
        """
        self._check_child_to_be_added(child)
        child._parent = self
        self._children.append(child)
        self._reset_iterators()
        if self._is_leaf is True:
            self._is_leaf = False
        return child

    def get_children(self) -> List['Tree']:
        """
        :obj:`~tree.tree.Tree` method

        :return: list of added children.
        :rtype: List[:obj:`~tree.tree.Tree`]
        """
        return self._children

    def get_children_of_type(self, type) -> List['Tree']:
        """
        :obj:`~tree.tree.Tree` method

        :return: list of added children of type.
        :rtype: List[:obj:`~tree.tree.Tree`]
        """
        return [ch for ch in self.get_children() if isinstance(ch, type)]

    def get_coordinates_in_tree(self) -> str:
        """
        :obj:`~tree.tree.Tree` method

        :return: 0 for ``root``. 1, 2, ... for layer 1. Other layers: x.y.z.... Example: 3.2.2 => third child of secod child of second child
                 of the root.
        :rtype: str

        >>> class TestTree(Tree):
        ...   def _check_child_to_be_added(self, child):
        ...      return True
        >>> root = TestTree()
        >>> root.get_coordinates_in_tree()
        '0'
        >>> child1 = root.add_child(TestTree())
        >>> child2 = root.add_child(TestTree())
        >>> grandchild1 = child2.add_child(TestTree())
        >>> grandchild2 = child2.add_child(TestTree())
        >>> child1.get_coordinates_in_tree()
        '1'
        >>> child2.get_coordinates_in_tree()
        '2'
        >>> grandchild1.get_coordinates_in_tree()
        '2.1'
        >>> grandchild2.get_coordinates_in_tree()
        '2.2'
        """
        if self.get_level() == 0:
            return '0'
        elif self.get_level() == 1:
            return str(self.get_parent().get_children().index(self) + 1)
        else:
            return f"{self.get_parent().get_coordinates_in_tree()}.{self.get_parent().get_children().index(self) + 1}"

    # def get_indentation(self) -> str:
    #     """
    #     :obj:`~tree.tree.Tree` method
    #
    #     :return: indentation according to ``get_level()`` (layer number). As default it is used for creating tabs in :obj:`tree_representation`
    #     :rtype: str
    #     """
    #     indentation = ''
    #     for i in range(self.get_level()):
    #         indentation += '    '
    #     return indentation
    def filter_nodes(self, key:Union[Callable], return_value) -> list:
        """
        :obj:`~tree.tree.Tree` method

        >>> t = TestTree('root')
        >>> t.filter_nodes(lambda node: node.get_level(), 2)
        [grandchild1, grandchild2, grandchild3]
        """
        output = []

        for node in self.traverse():
            if key(node) == return_value:
                output.append(node)
        return output

    def get_parent(self) -> 'Tree':
        """
        :obj:`~tree.tree.Tree` method

        :return: parent. ``None`` for ``root``.
        :rtype: :obj:`~tree.tree.Tree`
        """
        return self._parent

    def get_leaves(self, key: Optional[Callable] = None) -> list:
        """
        :obj:`~tree.tree.Tree` method

        :param key: An optional callable to be called on each leaf.
        :return: nested list of leaves or values of key(leaf) for each leaf
        :rtype: nested list of :obj:`~tree.tree.Tree`
        """
        output = []
        for child in self.get_children():
            if not child.is_leaf:
                output.append(child.get_leaves(key=key))
            else:
                if key is not None:
                    output.append(key(child))
                else:
                    output.append(child)

        return output

    def get_root(self) -> 'Tree':
        """
        :obj:`~tree.tree.Tree` method

        :return: ``root`` (upmost node of a tree which has no parent)
        :rtype: :obj:`~tree.tree.Tree`

        >>> t = TestTree('root')
        >>> t.greatgrandchild1.get_root() == t
        True
        >>> t.child4.get_root() == t
        True
        >>> t.get_root() == t
        True
        """
        node = self
        parent = node.get_parent()
        while parent is not None:
            node = parent
            parent = node.get_parent()
        return node

    def get_layer(self, level: int, key: Optional[Callable] = None) -> list:
        """
        :obj:`~tree.tree.Tree` method

        :param level: layer number where 0 is the ``root``.
        :param key: An optional callable for each node in the layer.
        :return: All nodes on this get_level. The leaves of branches which are shorter than the given get_level will be repeated on this and all
                 following layers.
        :rtype: list
        """
        if level == 0:
            output = [self]
        elif level == 1:
            output = self.get_children()
        else:
            output = []
            for child in self.get_layer(level - 1):
                if child.is_leaf:
                    output.append(child)
                else:
                    output.extend(child.get_children())
        if key is None:
            return output
        else:
            return [key(child) for child in output]

    def iterate_leaves(self) -> Iterator['Tree']:
        """
        :obj:`~tree.tree.Tree` method

        :return: A generator iterating over all leaves.
        """
        if self._iterated_leaves is None:
            self._iterated_leaves = [n for n in self.traverse() if n.is_leaf]
        return iter(self._iterated_leaves)

    def remove(self, child: 'Tree') -> None:
        """
        :obj:`~tree.tree.Tree` method

        Child's parent will be set to ``None`` and child will be removed from list of children.

        :param child:
        :return: None
        """
        if child not in self.get_children():
            raise ChildNotFoundError
        child._parent = None
        self.get_children().remove(child)
        self._reset_iterators()

    def remove_children(self) -> None:
        """
        :obj:`~tree.tree.Tree` method

        Calls :obj:`remove()` on all children.

        :return: None
        """
        for child in self.get_children()[:]:
            child.up.remove(child)

    def replace_child(self, old, new, index: int = 0) -> None:
        """
        :obj:`~tree.tree.Tree` method

        :param old: child or function
        :param new: child
        :param index: index of old child in the list of its appearances
        :return: None
        """
        if hasattr(old, '__call__'):
            list_of_olds = [ch for ch in self.get_children() if old(ch)]
        else:
            list_of_olds = [ch for ch in self.get_children() if ch == old]
        if not list_of_olds:
            raise ValueError(f"{old} not in list.")
        self._check_child_to_be_added(new)
        old_index = self.get_children().index(list_of_olds[index])
        old_child = self.get_children()[old_index]
        self.get_children().remove(old_child)
        self.get_children().insert(old_index, new)
        old_child._parent = None
        self._reset_iterators()
        new._parent = self

    def get_reversed_path_to_root(self) -> Iterator['Tree']:
        """
        :obj:`~tree.tree.Tree` method

        :return: path from self upwards through all ancestors up to the ``root``.

        >>> t = TestTree('root')
        >>> list(t.greatgrandchild1.get_reversed_path_to_root())
        [greatgrandchild1, grandchild2, child2, root]
        """
        if self._reversed_path_to_root is None:
            self._reversed_path_to_root = list(self._raw_reversed_path_to_root())
        return self._reversed_path_to_root

    def traverse(self) -> Iterator['Tree']:
        """
        :obj:`~tree.tree.Tree` method

        Traverse all tree nodes.

        :return: generator
        """
        if self._traversed is None:
            self._traversed = list(self._raw_traverse())
        return iter(self._traversed)

    def tree_representation(self, key: Optional[Callable] = None) -> str:
        """
        :obj:`~tree.tree.Tree` method

        :param key: An optional callable if ``None`` :obj:`~compact_repr` property of each node is called.
        :return: a representation of all nodes as string in tree form.
        :rtype: str

        >>> t = TestTree('root')
        t.tree_representation()
        └── root
            ├── child1
            ├── child2
            │   ├── grandchild1
            │   └── grandchild2
            │       └── greatgrandchild1
            ├── child3
            └── child4
                └── grandchild3
        """
        last_hook = '└'
        continue_hook = '├'
        no_hook = '│'
        horizontal = '── '
        space = '   '

        def get_vertical(node):
            return continue_hook

        def get_horizontal(node):
            return space

        def get_path(node):
            output = ''
            for n in node.get_reversed_path_to_root():
                if n.is_last_child:
                    pass
            return output

        if not key:
            key = lambda x: x.compact_repr

        output = ''
        for node in self.traverse():
            output += get_path(node)
            output += get_vertical(node) + get_horizontal(node) + key(node) + '\n'
        return output


class TestTree(Tree):
    def __init__(self, name=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        if self.name == 'root':
            self.child1 = self.add_child('child1')
            self.child2 = self.add_child('child2')
            self.child3 = self.add_child('child3')
            self.child4 = self.add_child('child4')
            self.grandchild1 = self.child2.add_child('grandchild1')
            self.grandchild2 = self.child2.add_child('grandchild2')
            self.grandchild3 = self.child4.add_child('grandchild3')
            self.greatgrandchild1 = self.grandchild2.add_child('greatgrandchild1')

    def _check_child_to_be_added(self, child):
        if not isinstance(child, self.__class__):
            raise TypeError

    def add_child(self, name):
        child = type(self)(name=name)
        return super().add_child(child)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()
