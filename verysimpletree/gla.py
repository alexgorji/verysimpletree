from typing import Any

from verysimpletree.tree import Tree, T


class TreeContent:
    pass


class FractalTreeContent:
    def __init__(self, value: int, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._value: int
        self.value = value

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, val: int) -> None:
        self._value = val


class FractalTree(Tree[Any]):
    def __init__(self, content: FractalTreeContent, *args: Any, **kwargs: Any) -> None:
        super().__init__(content, *args, **kwargs)

    def _check_child_to_be_added(self, child: Tree[Any]) -> bool:
        return True

    def generate_children(self) -> None:
        for child in [FractalTree(FractalTreeContent(value=self.content.value * i)) for i in range(1, 3)]:
            self.add_child(child)

    def add_child(self, child: T) -> T:
        self._children.append(child)
        print(child.content.value)
        return child


ft: FractalTree = FractalTree(FractalTreeContent(value=10))
ft.add_child(FractalTree(FractalTreeContent(value=20)))
ft.add_child(FractalTree(FractalTreeContent(value=30)))
ch1: FractalTree = ft.get_children()[0]
ch2: FractalTree = ft.get_children()[1]

ch21: FractalTree = ch2.add_child(FractalTree(FractalTreeContent(50)))

ft.generate_children()
ch3: FractalTree = ft.get_children()[2]
contents: list[FractalTreeContent] = [ch.content for ch in ft.get_children()]
print(contents)

print(ft.get_tree_representation(key=lambda node: node.content.value))
