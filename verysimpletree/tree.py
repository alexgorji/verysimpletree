from abc import ABC, abstractmethod
from typing import Optional, Callable, Iterator, TypeVar, Any, Generic, cast, Union


class TreeException(Exception):
    pass


class ChildNotFoundError(TreeException):
    pass


T = TypeVar('T', bound='Tree')


class Tree(ABC, Generic[T]):
    """
    An abstract lightweight tree class for managing tree structures in MusicXML and musicscore packages.
    """
    _TREE_ATTRIBUTES = {'compact_repr', 'is_leaf', 'is_last_child', 'is_root', '_parent', '_children',
                        'up'}

    def __init__(self: T, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._parent: Optional['T'] = None
        self._children: list['T'] = []
        self._traversed: Optional[list['T']] = None
        self._iterated_leaves: Optional[list['T']] = None
        self._reversed_path_to_root: Optional[list['T']] = None
        self._is_leaf: bool = True

    @abstractmethod
    def _check_child_to_be_added(self: T, child):
        """each child must be checked before being added to the Tree"""

    def _raw_traverse(self: T) :
        yield self
        for child in self.get_children():
            for node in child._raw_traverse():
                yield node

    def _raw_reversed_path_to_root(self: T) :
        yield self
        if self.get_parent():
            for node in self.get_parent().get_reversed_path_to_root():
                yield node

    def _reset_iterators(self: T) :
        """
        This method is used to reset both parent's and this class's iterators for :obj:'~traverse', obj:'~iterate_leaves' and obj:'~get_reversed_path_to_root'
        """
        if self.up:
            self.up._reset_iterators()
        self._traversed = None
        self._iterated_leaves = None
        self._reversed_path_to_root = None

    @property
    def is_last_child(self: T) :
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
    def is_leaf(self: T)  -> bool:
        """
        :obj:`~tree.tree.Tree` property

        :return: ``True`` if self has no children. ``False`` if self has one or more children.
        :rtype: bool
        """
        return self._is_leaf

    @property
    def is_root(self: T)  -> bool:
        """
        :obj:`~tree.tree.Tree` property

        :return: ``True`` if self has no parent, else ``False``.
        :rtype: bool
        """
        return True if self.get_parent() is None else False

    def get_level(self: T)  -> int:
        """
        :obj:`~tree.tree.Tree`

        :return: ``0`` for ``root``, ``1, 2 etc.`` for each layer of children
        :rtype: nonnegative int

        >>> root.get_level()
        0
        >>> child1.get_level()
        1
        >>> grandchild1.get_level()
        2
        >>> greatgrandchild1.get_level()
        3
        """
        parent = self.get_parent()
        if parent is None:
            return 0
        else:
            return parent.get_level() + 1

    @property
    def next(self: 'T') -> Optional['T']:
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
    def previous(self: 'T') -> Optional['T']:
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
    def up(self: 'T') -> Optional[T]:
        """
        :obj:`~tree.tree.Tree` property

        :return: :obj:`get_parent()`
        :rtype: :obj:`~tree.tree.Tree`
        """
        return self.get_parent()

    def add_child(self: T, child: 'T') -> 'T':
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

    def get_children(self: T) -> list['T']:
        """
        :obj:`~tree.tree.Tree` method

        :return: list of added children.
        """
        return self._children

    def get_children_of_type(self: T, type_: type) -> list['T']:
        """
        :obj:`~tree.tree.Tree` method

        :return: list of added children of type.d
        :rtype: list[:obj:`~tree.tree.Tree`]
        """
        return [cast(T, ch) for ch in self.get_children() if isinstance(ch, type_)]

    def get_position_in_tree(self: T) -> str:
        """
        :obj:`~tree.tree.Tree` method

        :return: 0 for ``root``. 1, 2, ... for layer 1. Other layers: x.y.z.... Example: 3.2.2 => third child of secod child of second child
                 of the root.
        :rtype: str

        >>> print(root.get_tree_representation(key=lambda node: node.get_position_in_tree()))
        └── 0
            ├── 1
            ├── 2
            │   ├── 2.1
            │   │   ├── 2.1.1
            │   │   └── 2.1.2
            │   └── 2.2
            ├── 3
            └── 4
                └── 4.1
        <BLANKLINE>
        """
        parent = self.get_parent()
        if parent is None:
            return '0'
        elif self.get_level() == 1:
            return str(parent.get_children().index(self) + 1)
        else:
            return f"{parent.get_position_in_tree()}.{parent.get_children().index(self) + 1}"

    def get_distance(self: T, reference: Optional['T'] = None) -> Optional[int]:
        """
        >>> root.get_distance()
        0
        >>> greatgrandchild1.get_distance()
        3
        >>> greatgrandchild1.get_distance(child2)
        2
        >>> print(greatgrandchild1.get_distance(child1))
        None
        """

        if self.is_root:
            return 0

        if reference is None:
            reference = self.get_root()

        parent = self.up
        count = 1
        while parent is not reference:
            parent = parent.up  # type: ignore
            count += 1
            if parent.is_root and parent is not reference:  # type: ignore
                return None
        return count

    def get_farthest_leaf(self: 'T') -> 'T':
        """
        >>> root.get_farthest_leaf()
        greatgrandchild1
        """
        leaves: list[T] = list(self.iterate_leaves())
        if not leaves:
            leaves = [self]
        return max(leaves, key=lambda leaf: leaf.get_distance())  # type: ignore

    def filter_nodes(self: T, key: Callable[['T'], Any], return_value: Any) -> list['T']:
        """
        :obj:`~tree.tree.Tree` method

        >>> root.filter_nodes(lambda node: node.get_level(), 2)
        [grandchild1, grandchild2, grandchild3]
        """
        output = []

        for node in self.traverse():
            if key(node) == return_value:
                output.append(node)
        return output

    def get_parent(self: 'T') -> Optional[T]:
        """
        :obj:`~tree.tree.Tree` method

        :return: parent. ``None`` for ``root``.
        :rtype: :obj:`~tree.tree.Tree`
        """
        return self._parent

    def get_leaves(self: T, key: Optional[Callable[['T'], Any]] = None) -> list[
        Union[Any, list[Any]]]:
        """
        Tree method

        :param key: An optional callable to be called on each leaf.
        :return: nested list of leaves or values of key(leaf) for each leaf

        >>> root.get_leaves()
        [child1, [[greatgrandchild1, greatgrandchild2], grandchild2], child3, [grandchild3]]
        """
        output: list[Union[Any, list[Any]]] = []
        child: 'T'
        for child in self.get_children():
            if not child.is_leaf:
                output.append(child.get_leaves(key=key))
            else:
                if key is not None:
                    output.append(key(child))
                else:
                    output.append(child)
        if not output:
            if key is not None:
                return [key(self)]
            else:
                return [cast(list[Any], self)]
        return output

    def get_root(self: T) -> 'T':
        """
        :obj:`~tree.tree.Tree` method

        :return: ``root`` (upmost node of a tree which has no parent)
        :rtype: :obj:`~tree.tree.Tree`

        >>> greatgrandchild1.get_root() == root
        True
        >>> child4.get_root() == root
        True
        >>> root.get_root() == root
        True
        """
        node = self
        parent = node.get_parent()
        while parent is not None:
            node = parent
            parent = node.get_parent()
        return node

    def get_self_with_key(self: T, key=None):
        if key is None:
            return self
        elif isinstance(key, str):
            return getattr(self, key)
        elif callable(key):
            return key(self)
        else:
            raise TypeError(f'{self.__class__}: key: {key} must be None, string or a callable object')

    def get_layer(self: T, level: int, key: Optional[Callable[['T'], Any]] = None) -> list['T']:
        """
        :obj:`~tree.tree.Tree` method

        :param level: layer number where 0 is the ``root``.
        :param key: An optional callable for each node in the layer.
        :return: All nodes on this level. The leaves of branches which are shorter than the given level will be repeated on this and all
                 following layers.
        :rtype: list
        """
        output: list['T']

        if level == 0:
            output = [cast(T, self)]
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

    def get_number_of_layers(self: T) -> int:
        """
        >>> root.get_number_of_layers()
        3
        """
        distance = self.get_farthest_leaf().get_distance(self)

        if not distance:
            return 0
        else:
            return distance

    def iterate_leaves(self: T) -> Iterator[T]:
        """
        :obj:`~tree.tree.Tree` method

        :return: A generator iterating over all leaves.
        """
        if self._iterated_leaves is None:  # Ensure self._iterated_leaves is not None
            self._iterated_leaves = [n for n in self.traverse() if n.is_leaf]

        return iter(self._iterated_leaves)

    def remove(self: T, child: 'T') -> None:
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

    def remove_children(self: T) -> None:
        """
        :obj:`~tree.tree.Tree` method

        Calls :obj:`remove()` on all children.

        :return: None
        """
        for child in self.get_children()[:]:
            parent = child.get_parent()
            if parent is not None:
                parent.remove(child)

    def replace_child(self: T, old, new, index: int = 0) -> None:
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

    def get_reversed_path_to_root(self: T) -> list['T']:
        """
        :obj:`~tree.tree.Tree` method

        :return: path from self upwards through all ancestors up to the ``root``.

        >>> greatgrandchild1.get_reversed_path_to_root()
        [greatgrandchild1, grandchild1, child2, root]
        """
        if self._reversed_path_to_root is None:
            self._reversed_path_to_root = list(self._raw_reversed_path_to_root())
        return self._reversed_path_to_root

    def traverse(self: T) -> Iterator['T']:
        """
        :obj:`~tree.tree.Tree` method

        Traverse all tree nodes.

        :return: generator
        """
        if self._traversed is None:
            self._traversed = list(self._raw_traverse())
        return iter(self._traversed)

    def get_tree_representation(self: T, key: Optional[Callable] = None, space=None) -> str:
        """
        :obj:`~tree.tree.Tree` method

        :param key: An optional callable if ``None`` :obj:`~compact_repr` property of each node is called.
        :return: a representation of all nodes as string in tree form.

        >>> print(root.get_tree_representation())
        └── root
            ├── child1
            ├── child2
            │   ├── grandchild1
            │   │   ├── greatgrandchild1
            │   │   └── greatgrandchild2
            │   └── grandchild2
            ├── child3
            └── child4
                └── grandchild3
        <BLANKLINE>
        """

        tree_representation = TreeRepresentation(tree=self)
        if key:
            tree_representation.key = key
        if space:
            tree_representation.space = space
        return tree_representation.get_representation()


class TreeRepresentation:
    def __init__(self: T, tree: T, key: Callable[['T'], Any] = lambda x: str(x), space: int = 3):
        self._tree: T = tree
        self._key: Callable[['T'], Any] = key
        self._space: int = space

    @property
    def tree(self: T):
        return self._tree

    @tree.setter
    def tree(self: T, val: T) -> None:
        self._tree = val

    @property
    def key(self: T) -> Callable[['T'], Any]:
        return self._key

    @key.setter
    def key(self: T, val: Callable[['T'], Any]) -> None:
        self._key = val

    @property
    def space(self: T) -> int:
        return self._space

    @space.setter
    def space(self: T, val: int) -> None:
        if not isinstance(val, int):
            raise TypeError('TreeRepresentation.space must be of type int')
        if val < 1:
            raise ValueError('TreeRepresentation.space must be greater than 0')
        self._space = val

    def get_representation(self: T) -> str:
        """
        >>> rep = TreeRepresentation(tree=root, key=lambda node: node.get_position_in_tree())
        >>> print(rep.get_representation())
        └── 0
            ├── 1
            ├── 2
            │   ├── 2.1
            │   │   ├── 2.1.1
            │   │   └── 2.1.2
            │   └── 2.2
            ├── 3
            └── 4
                └── 4.1
        <BLANKLINE>
        >>> rep = TreeRepresentation(tree=root, key=lambda node: node.get_position_in_tree(), space=1)
        >>> print(rep.get_representation())
        └ 0
          ├ 1
          ├ 2
          │ ├ 2.1
          │ │ ├ 2.1.1
          │ │ └ 2.1.2
          │ └ 2.2
          ├ 3
          └ 4
            └ 4.1
        <BLANKLINE>

        """

        last_hook = '└'
        continue_hook = '├'
        no_hook = '│'
        horizontal = '─'

        def get_vertical():
            if node.is_last_child:
                return last_hook
            return continue_hook

        def get_horizontal():
            return (horizontal * (self.space - 1)) + ' '

        def get_path():
            path = ''
            for i, n in enumerate(node.get_reversed_path_to_root()):
                if i == 0:
                    pass
                else:
                    if n.is_last_child:
                        path = (self.space + 1) * ' ' + path
                    else:
                        path = no_hook + (self.space * ' ') + path
            return path

        output = ''
        for node in self.tree.traverse():
            output += get_path()
            output += get_vertical() + get_horizontal() + str(self.key(node)) + '\n'
        return output


# Example usage
class TestTree(Tree):

    def __init__(self, name: str = '', *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.name = name

    def _check_child_to_be_added(self, child: 'TestTree'):
        if not isinstance(child, self.__class__):
            raise TypeError

    def add_child(self, name) -> 'TestTree':
        child: 'T' = self.__class__(name=name)
        return super().add_child(child)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()


root = TestTree('root')
child1: TestTree = root.add_child('child1')
child2: TestTree = root.add_child('child2')
child3: TestTree = root.add_child('child3')
child4: TestTree = root.add_child('child4')
grandchild1: TestTree = child2.add_child('grandchild1')
grandchild2: TestTree = child2.add_child('grandchild2')
grandchild3: TestTree = child4.add_child('grandchild3')
greatgrandchild1: TestTree = grandchild1.add_child('greatgrandchild1')
greatgrandchild2: TestTree = grandchild1.add_child('greatgrandchild2')
