from src.restaurant_card import RestaurantRootCard
from src.tds_card import TDSRootCard


def merge_cards(key: str, card_list: list) -> TDSRootCard:
    """
    Merges the Cards in the list of cards and returns a RootCard
    :param key: the key for the root Card.
    :param card_list: the list of Cards to merge
    :return: a root Card
    """
    # Create a new card with given key
    root_card = TDSRootCard(card_type=key)

    # Add all sub-cards
    for card in card_list:
        root_card.add(card)

    # Initialize the root card based on the children cards
    root_card.sort_card()

    # Return the root Card
    return root_card


def merge_restaurant_cards(key: str, card_list: list) -> RestaurantRootCard:
    """
    Merges the Cards in the list of cards and returns a RootCard
    :param key: the key for the root Card.
    :param card_list: the list of Cards to merge
    :return: a root Card
    """
    # Create a new card with given key
    root_card = RestaurantRootCard(card_type=key)

    # Add all sub-cards
    for card in card_list:
        root_card.add(card)

    # Initialize the root card based on the children cards
    root_card.sort_card()

    # Return the root Card
    return root_card
