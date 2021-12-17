from src.base_card import CardMetaData
from src.composite_card import (CompositeCard, LeafCard)


class RestaurantRootCard(CompositeCard):
    """
    A root class represent a common class that encapsulates
    the content of all (sub) classes under this Card.
    """
    def __init__(self, card_type: str):
        super().__init__(CardMetaData("Yelp"))

        # Type of this root card: article, blog, etc.
        self.card_type = card_type

        # Title of the top-ranked Card among all children Cards
        self.top_ranked_result_name = ""

        # URL of the top-ranked Card among all children Cards
        self.top_ranked_result_url = ""

        # Top score
        self.top_ranked_score = 0

        # Review matching the query
        self.top_ranked_review = ""

    def sort_card(self):
        """
        Compute the top-ranked Card.
        :return: None
        """
        for card in self._children:
            if card.score > self.top_ranked_score:
                self.top_ranked_score = card.score

                # Set top-ranked Card data
                self.top_ranked_result_name = card.info["name"]
                self.top_ranked_result_url = card.info["url"]
                self.top_ranked_review = card.context


class RestaurantCard(LeafCard):
    """
    A leaf card encapsulating information representing a restaurant.
    """
    def __init__(self, query: str, card_data: dict):
        super().__init__(CardMetaData("Yelp"))

        # The query producing this Card as a result
        self.search_query = query

        # This Card's score w.r.t. the query
        self.score = card_data['score']

        # The full information
        self.card_meta = card_data["meta"]
        self.context = card_data["context"]
        self.info = card_data["info"]
