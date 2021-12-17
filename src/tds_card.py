from src.base_card import CardMetaData
from src.composite_card import (CompositeCard, LeafCard)
from src.utils import run_wikifier


class TDSRootCard(CompositeCard):
    """
    A root class represent a common class that encapsulates
    the content of all (sub) classes under this Card.
    """
    def __init__(self, card_type: str):
        super().__init__(CardMetaData("TowardsDataScience"))

        # Type of this root card: article, blog, etc.
        self.card_type = card_type

        # Title of the top-ranked Card among all children Cards
        self.top_ranked_result_title = ""

        # URL of the top-ranked Card among all children Cards
        self.top_ranked_result_url = ""

    def sort_card(self):
        """
        Compute the top-ranked Card.
        :return: None
        """
        top_score = 0
        for card in self._children:
            if card.score > top_score:
                top_score = card.score

                # Set top-ranked Card title and URL
                self.top_ranked_result_title = card.card_data["title"]
                self.top_ranked_result_url = card.card_data["url"]


class TDSCard(LeafCard):
    """
    A leaf card encapsulating information from a TDS article.
    """
    def __init__(self, query: str, card_data: dict):
        super().__init__(CardMetaData("TowardsDataScience"))

        # The query producing this Card as a result
        self.search_query = query

        # This Card's score w.r.t. the query
        self.score = card_data['score']

        # List of related concepts to this Card.
        # Computed on demand
        self.related_concepts = list()

        # URL of the image to display with this Card
        self.image = card_data['image']

        # The full information
        self.card_data = card_data

    def open_card(self):
        if self.related_concepts:
            # Use cached data
            return self.related_concepts

        # Prepare the text to send to the Wikifier service
        card_text = self.card_data["summary_prefix"] + '\n' + self.card_data["summary"]

        # Run the Wikifier
        all_entities = run_wikifier(card_text)
        all_entities = all_entities["entities"]
        if not all_entities:
            return

        for entity in all_entities:
            self.related_concepts.append(
                {
                    "title": entity["title"],
                    "label": entity["label"],
                    "url": entity["url"],
                }
            )
