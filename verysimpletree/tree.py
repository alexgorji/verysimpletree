from abc import ABC, abstractmethod
from typing import Optional, Callable, Iterator, TypeVar, Any, Generic, cast, Union

from verysimpletree.util import make_list


class TreeException(Exception):
    pass


class TreeReferenceError(TreeException, AttributeError):
    pass


class ChildNotFoundError(TreeException):
    pass


T = TypeVar('T', bound='Tree[Any]')


class Tree(ABC, Generic[T]):
    """
    An abstract lightweight tree class for managing tree structures in MusicXML and musicscore packages.
    """
    _TREE_ATTRIBUTES = {'is_leaf', 'is_last_child', 'is_root', '_parent', '_children',
                        'up', 'content'}

    def __init__(self, content: Any = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._content: Any
        self.content = content
        self._parent: Optional[T] = None
        self._children: list[T] = []
        self._traversed: Optional[list[T]] = None
        self._iterated_leaves: Optional[list[T]] = None
        self._reversed_path_to_root: Optional[list[T]] = None
        self._is_leaf: bool = True

    @abstractmethod
    def _check_child_to_be_added(self, child: T) -> bool:
        """each child must be checked before being added to the Tree"""

    def _raw_traverse(self: T) -> Iterator[T]:
        yield self
        for child in self.get_children():
            for node in child._raw_traverse():
                yield node

    def _raw_reversed_path_to_root(self: T) -> Iterator[T]:
        yield self
        parent = self.get_parent()
        if parent is not None:
            for node in parent.get_reversed_path_to_root():
                yield node

    def _reset_iterators(self) -> None:
        """
        This method is used to reset both parent's and this class's iterators for :obj:'~traverse', obj:'~iterate_leaves' and obj:'~get_reversed_path_to_root'
        """
        if self.up:
            self.up._reset_iterators()
        self._traversed = None
        self._iterated_leaves = None
        self._reversed_path_to_root = None

    @property
    def content(self) -> Any:
        return self._content

    @content.setter
    def content(self, value: Any) -> None:
        self._content = value

    @property
    def is_first_child(self) -> bool:
        if self.is_root:
            return True
        if cast(T, self.up).get_children()[0] == self:
            return True
        return False

    @property
    def is_last_child(self) -> bool:
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
        if cast(T, self.up).get_children()[-1] == self:
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

    @property
    def next(self) -> Optional[T]:
        """
        :obj:`~tree.tree.Tree` property

        :return: next sibling. ``None`` if this is the last current child of the parent.
        :rtype: :obj:`~tree.tree.Tree`
        """
        if self.up and self != self.up.get_children()[-1]:
            return cast(T, self.up.get_children()[self.up.get_children().index(self) + 1])
        else:
            return None

    @property
    def previous(self) -> Optional[T]:
        """
        :obj:`~tree.tree.Tree` property

        :return: previous sibling. ``None`` if this is the first child of the parent.
        :rtype: :obj:`~tree.tree.Tree`
        """
        if self.up and self != self.up.get_children()[0]:
            return cast(T, self.up.get_children()[self.up.get_children().index(self) - 1])
        else:
            return None

    @property
    def up(self) -> Optional[T]:
        """
        :obj:`~tree.tree.Tree` property

        :return: :obj:`get_parent()`
        :rtype: :obj:`~tree.tree.Tree`
        """
        return self.get_parent()

    def add_child(self, child: T) -> T:
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
    
    # typing with T and Generic[T] etc. seems to be faulty. Return value of _create_node is Tree[T].
    @classmethod
    def create_tree_from_list(cls, tree_list_representation: list[list[Any]], represented_attribute_names: list[str]) -> T:
        represented_attribute_names = make_list(represented_attribute_names)
        def _create_node(represented_values: list[Any]) -> T:
            if len(represented_values) != len(represented_attribute_names):
                raise ValueError(f'create_tree_from_list: represented_attribute_names must be of length {len(represented_values)}.')
            root_kwargs = {attr:val for attr, val in zip(represented_attribute_names, represented_values)}
            return cast(T, cls(**root_kwargs))
        node = _create_node(make_list(tree_list_representation[0]))
        for child_list_representation in tree_list_representation [1:]:
            child = cls.create_tree_from_list(child_list_representation, represented_attribute_names)
            node.add_child(child)
        return node
    
    def get_children(self: T) -> list[T]:
        """
        :obj:`~tree.tree.Tree` method

        :return: list of added children.
        """
        return self._children

    def get_children_of_type(self, type_: type) -> list[T]:
        """
        :obj:`~tree.tree.Tree` method

        :return: list of added children of type.d
        :rtype: list[:obj:`~tree.tree.Tree`]
        """
        return [cast(T, ch) for ch in self.get_children() if isinstance(ch, type_)]

    def get_distance(self, reference: Optional[T] = None) -> int:
        """
        >>> root.get_distance()
        0
        >>> greatgrandchild1.get_distance()
        3
        >>> greatgrandchild1.get_distance(child2)
        2
        """

        if self.is_root:
            return 0

        if reference is None:
            reference = self.get_root()

        parent = self.up
        count = 1
        while parent is not None and parent is not reference:
            parent = parent.up
            count += 1
            if parent is not None and parent.is_root and parent is not reference:
                raise TreeReferenceError(f"Wrong reference {reference} not in path to root.")
        return count

    def get_farthest_leaf(self: T) -> T:
        """
        >>> root.get_farthest_leaf()
        greatgrandchild1
        """
        leaves: list[T] = list(self.iterate_leaves())
        return max(leaves, key=lambda leaf: leaf.get_distance())

    def get_layer(self: T, level: int, key: Optional[Callable[[T], Any]] = None) -> Any:
        """
        :obj:`~tree.tree.Tree` method

        :param level: layer number where 0 is the ``root``.
        :param key: An optional callable for each node in the layer.
        :return: All nodes on this level. The leaves of branches which are shorter than the given level will be repeated on this and all
                 following layers.
        :rtype: list
        """
        output: Any

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
            if level == 0:
                return key(output)
            else:
                return [key(child) for child in output]

    def get_leaves(self, key: Optional[Callable[[T], Any]] = None) -> list[Union[Any, list[Any]]]:
        """
        Tree method

        :param key: An optional callable to be called on each leaf.
        :return: nested list of leaves or values of key(leaf) for each leaf

        >>> root.get_leaves()
        [child1, [[greatgrandchild1, greatgrandchild2], grandchild2], child3, [grandchild3]]
        """
        output: list[Union[Any, list[Any]]] = []
        child: T
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
                return [key(cast(T, self))]
            else:
                return [cast(T, self)]
        return output

    def get_level(self) -> int:
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

    def get_parent(self: T) -> Optional[T]:
        """
        :obj:`~tree.tree.Tree` method

        :return: parent. ``None`` for ``root``.
        :rtype: :obj:`~tree.tree.Tree`
        """
        return self._parent

    def get_position_in_tree(self) -> str:
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

    def get_reversed_path_to_root(self) -> list[T]:
        """
        :obj:`~tree.tree.Tree` method

        :return: path from self upwards through all ancestors up to the ``root``.

        >>> greatgrandchild1.get_reversed_path_to_root()
        [greatgrandchild1, grandchild1, child2, root]
        """
        if self._reversed_path_to_root is None:
            self._reversed_path_to_root = list(self._raw_reversed_path_to_root())
        return self._reversed_path_to_root

    def get_root(self: T) -> T:
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

    def get_self_with_key(self, key: Optional[Callable[[T], Any]] = None) -> Any:
        if key is None:
            return self
        elif isinstance(key, str):
            return getattr(self, key)
        elif callable(key):
            return key(cast(T, self))
        else:
            raise TypeError(f'{self.__class__}: key: {key} must be None, string or a callable object')

    def get_tree_representation(self, key: Optional[Callable[[T], Any]] = None, space: int = 3) -> str:
        """
        :obj:`~tree.tree.Tree` method

        :param key: An optional callable if ``None`` string(node) is called.
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

        tree_representation = TreeRepresentation(tree=self, space=space)
        if key:
            tree_representation.key = cast(Callable[[Tree[Any]], Any], key)
        return tree_representation.get_representation()
    
    def get_list_representation(self, key: Callable[["Tree[T]"], Any]) -> list[list[Any]]:
        result: list[list[Any]] = [key(self)]
        for child in self.get_children():
            result.append(child.get_list_representation(key=key))
        return result

    def get_number_of_layers(self) -> int:
        """
        >>> root.get_number_of_layers()
        3
        """
        distance = self.get_farthest_leaf().get_distance(self)

        if not distance:
            return 0
        else:
            return distance

    def filter_nodes(self, key: Callable[[T], Any], return_value: Any) -> list[T]:
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

    def iterate_leaves(self) -> Iterator[T]:
        """
        :obj:`~tree.tree.Tree` method

        :return: A generator iterating over all leaves.
        """
        if self._iterated_leaves is None:  # Ensure self._iterated_leaves is not None
            self._iterated_leaves = [n for n in self.traverse() if n.is_leaf]

        return iter(self._iterated_leaves)

    def remove(self, child: T) -> None:
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
            parent = child.get_parent()
            if parent is not None:
                parent.remove(child)

    def replace_child(self, old: T, new: T, index: int = 0) -> None:
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

    def traverse(self) -> Iterator[T]:
        """
        :obj:`~tree.tree.Tree` method

        Traverse all tree nodes.

        :return: generator
        """
        if self._traversed is None:
            self._traversed = list(self._raw_traverse())
        return iter(self._traversed)


class TreeRepresentation:
    def __init__(self, tree: Tree[Any], key: Callable[[Tree[Any]], Any] = lambda x: str(x), space: int = 3):
        self._tree: Tree[Any]
        self._key: Callable[[Tree[Any]], Any]
        self._space: int
        self.tree = tree
        self.key = key
        self.space = space

    @property
    def tree(self) -> Tree[Any]:
        return self._tree

    @tree.setter
    def tree(self, val: Tree[Any]) -> None:
        self._tree = val

    @property
    def key(self) -> Callable[[Tree[Any]], Any]:
        return self._key

    @key.setter
    def key(self, val: Callable[[Tree[Any]], Any]) -> None:
        self._key = val

    @property
    def space(self) -> int:
        return self._space

    @space.setter
    def space(self, val: int) -> None:
        if not isinstance(val, int):
            raise TypeError('TreeRepresentation.space must be of type int')
        if val < 1:
            raise ValueError('TreeRepresentation.space must be greater than 0')
        self._space = val

    def get_representation(self) -> str:
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

        last_hook: str = '└'
        continue_hook: str = '├'
        no_hook: str = '│'
        horizontal: str = '─'

        def get_vertical() -> str:
            if node.is_last_child:
                return last_hook
            return continue_hook

        def get_horizontal() -> str:
            return (horizontal * (self.space - 1)) + ' '

        def get_path() -> str:
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
class TestTree(Tree[Any]):  # pragma: no cover

    def __init__(self, name: str = '', *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.name = name

    def _check_child_to_be_added(self, child: T) -> bool:
        if not isinstance(child, Tree):
            raise TypeError
        return True

    def add_string_child(self, name: str) -> 'TestTree':
        child: 'TestTree' = self.__class__(name=name)
        return cast(TestTree, self.add_child(child))

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()


root = TestTree('root')
child1: TestTree = root.add_string_child('child1')
child2: TestTree = root.add_string_child('child2')
child3: TestTree = root.add_string_child('child3')
child4: TestTree = root.add_string_child('child4')
grandchild1: TestTree = child2.add_string_child('grandchild1')
grandchild2: TestTree = child2.add_string_child('grandchild2')
grandchild3: TestTree = child4.add_string_child('grandchild3')
greatgrandchild1: TestTree = grandchild1.add_string_child('greatgrandchild1')
greatgrandchild2: TestTree = grandchild1.add_string_child('greatgrandchild2')
