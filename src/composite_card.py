from __future__ import annotations
from src.base_card import (BaseCard, CardMetaData)


class ComponentCard(BaseCard):
    """
    The base Component class in a Composite pattern.
    """
    def __init__(self, meta_data: CardMetaData):
        super().__init__(meta_data)

    @property
    def parent(self) -> ComponentCard:
        return self._parent

    @parent.setter
    def parent(self, parent: ComponentCard):
        """
        Optionally, the base Component can declare an interface for setting and
        accessing a parent of the component in a tree structure. It can also
        provide some default implementation for these methods.
        """
        self._parent = parent

    def add(self, component: ComponentCard) -> None:
        pass

    def remove(self, component: ComponentCard) -> None:
        pass

    def is_composite(self) -> bool:
        """
        Returns whether this Card is a composite or a leaf Card.
        :return: True if this Card is composite, False otherwise.
        """
        return False


class LeafCard(ComponentCard):
    """
    A LeafCard is a Card with no children.
    """
    def __init__(self, meta_data: CardMetaData):
        super().__init__(meta_data)


class CompositeCard(ComponentCard):
    """
    The CompositeCard is a Card that can have one or more children.
    Each child is a ComponentCard. This will recursively build a "tree"
    of Cards.
    """
    def __init__(self, meta_data: CardMetaData) -> None:
        super().__init__(meta_data)

        # All the children of this Card
        self._children = list()

    def add(self, component: ComponentCard) -> None:
        self._children.append(component)
        component.parent = self

    def remove(self, component: ComponentCard) -> None:
        self._children.remove(component)
        component.parent = None

    def is_composite(self) -> bool:
        return True

    def get_num_children(self) -> int:
        return len(self._children)

    def get_children(self) -> list:
        return self._children
