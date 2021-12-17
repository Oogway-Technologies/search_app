import uuid
from abc import ABC


class CardMetaData:
    """
    MetaData for Cards.
    """
    def __init__(self, name: str = ""):
        self.name = name


class BaseCard(ABC):
    """
    A parent base Card for any other type of Card.
    """
    def __init__(self, metadata: CardMetaData):
        # Parent card
        self._parent = None

        # Unique identifier for this card
        self._id = uuid.uuid4()

        # MetaData for this card
        self._metadata = metadata

    def get_unique_id(self) -> str:
        """
        Returns this card unique identifier.
        :return: this card's unique identifier.
        """
        return str(self._id)

    def get_metadata(self) -> CardMetaData:
        """
        Returns this card MetaData.
        :return: this card's MetaData
        """
        return self._metadata

    def get_parent(self):
        """
        Returns this Card's parent.
        :return: this Card's parent
        """
        return self._parent
