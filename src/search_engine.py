from src.card_utils import (merge_cards, merge_restaurant_cards)
from src.const import *
from src.restaurant_card import RestaurantCard
from src.tds_card import TDSCard
from src.utils import (call_qa_endpoint, call_search_endpoint, call_restaurant_endpoint)


def process_search(search_query: str, search_engine_type: TDSSearchEngineType, num_results_to_retrieve: int,
                   score_threshold: float = 0.65) -> list:
    # Call API based on the type of engine
    if search_engine_type == TDSSearchEngineType.BM_25:
        result = call_search_endpoint(endpoint=TDS_KEYWORD_SEARCH_ENDPOINT, search_query=search_query,
                                      num_results=num_results_to_retrieve)
    elif search_engine_type == TDSSearchEngineType.DPR:
        result = call_search_endpoint(endpoint=TDS_DPR_SEARCH_ENDPOINT, search_query=search_query,
                                      num_results=num_results_to_retrieve)
    else:
        num_results_to_retrieve = num_results_to_retrieve // 2
        result = call_search_endpoint(endpoint=TDS_MIX_SEARCH_ENDPOINT, search_query=search_query,
                                      num_results=num_results_to_retrieve)
    if not result:
        # Something went wrong
        return []

    # Filter out results with low score.
    # Otherwise, build corresponding result Card
    cards_collection = dict()
    for res in result["result"]:
        if res["score"] >= score_threshold:
            # Given a results, build the corresponding Card
            tds_card = TDSCard(search_query, res)

            # Store cards by they category: article, blog, how-to, etc.
            card_category = tds_card.card_data["category"]
            if card_category not in cards_collection:
                cards_collection[card_category] = list()
            cards_collection[card_category].append(tds_card)

    # Create a root category Card for each category
    root_cards_list = list()
    for key, card_list in cards_collection.items():
        root_card = merge_cards(key, card_list)
        root_cards_list.append(root_card)

    # Return the list of all root cards
    return root_cards_list


def process_qa(search_query: str, num_results_to_retrieve: int, num_results_reader: int):
    result = call_qa_endpoint(search_query=search_query, num_results=num_results_to_retrieve,
                              num_reader=num_results_reader)
    return result["result"]


def restaurant_search(search_query: str, num_results_to_retrieve: int):
    result = call_restaurant_endpoint(endpoint=RESTAURANT_SEARCH_ENDPOINT, search_query=search_query,
                                      num_results=num_results_to_retrieve, location_list=[])
    if not result:
        # Something went wrong
        return []

    cards_collection = dict()
    for res in result["result"]:
        # Given a results, build the corresponding Card
        res_card = RestaurantCard(search_query, res)

        # Store cards by they category: article, blog, how-to, etc.
        card_category = res_card.info["categories"][0]
        if card_category not in cards_collection:
            cards_collection[card_category] = list()
        cards_collection[card_category].append(res_card)

    # Create a root category Card for each category
    root_cards_list = list()
    for key, card_list in cards_collection.items():
        root_card = merge_restaurant_cards(key, card_list)
        root_cards_list.append(root_card)

    # Return the list of all root cards
    return root_cards_list
