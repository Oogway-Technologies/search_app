import json
import requests
from src.const import (QueryType, TDS_QA_ENDPOINT, WIKIFIER_ENDPOINT, WIKIFIER_THRESHOLD)


def get_query_type(query: str) -> QueryType:
    if not query:
        return QueryType.EMPTY_QUERY
    elif query.startswith('explore:'):
        return QueryType.EXPLORE_QUERY
    elif query.startswith('open:'):
        return QueryType.OPEN_QUERY
    elif query.startswith('res:'):
        return QueryType.RES_SEARCH_QUERY
    elif query.startswith('res-explore:'):
        return QueryType.RES_EXPLORE_QUERY
    elif query.startswith('res-open:'):
        return QueryType.RES_OPEN_QUERY
    else:
        return QueryType.SEARCH_QUERY


def is_bonus_query(query: str) -> bool:
    return query.startswith('res:')


def is_tds_qa(query: str):
    # Nothing really fancy here...
    return query[-1] == '?'


def call_search_endpoint(endpoint: str, search_query: str, num_results: int) -> dict:
    url = endpoint
    payload = json.dumps({
        "query": search_query,
        "num_results": num_results
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        return {}
    return json.loads(response.text)


def call_qa_endpoint(search_query: str, num_results: int, num_reader: int):
    url = TDS_QA_ENDPOINT

    payload = json.dumps({
        "query": search_query,
        "num_results": num_results,
        "num_reader": num_reader
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 200:
        return {}
    return json.loads(response.text)


def select_root_and_get_cards_list(query: str, root_card_list: list):
    card_type_list = query.split(':')
    if len(card_type_list) == 1 or not card_type_list[1]:
        return None
    card_type_list = card_type_list[1:]
    card_type_list = [x.strip() for x in card_type_list]
    card_type = ' '.join(card_type_list)
    for root_card in root_card_list:
        if card_type.strip().lower() == root_card.card_type.strip().lower():
            return root_card.get_children()

    # Try query without spaces
    card_type_no_space = card_type.replace(' ', '')
    for root_card in root_card_list:
        if card_type_no_space.strip().lower() == root_card.card_type.strip().lower().replace(' ', ''):
            return root_card.get_children()

    # Try starts with
    for root_card in root_card_list:
        if root_card.card_type.strip().lower().startswith(card_type.strip().lower()):
            return root_card.get_children()

    return None


def select_card_to_open(query: str, card_list: list):
    card_idx_list = query.split(':')
    if len(card_idx_list) == 1 or not card_idx_list[1]:
        return None
    try:
        card_idx = int(card_idx_list[1].strip())
    except:
        return None
    if card_idx < 0 or card_idx >= len(card_list):
        return None

    # Get the Card
    card = card_list[card_idx]

    # Explore the card
    card.open_card()

    # Return the opened card
    return card


def run_wikifier(text: str):
    text = text.replace('\n', ' ')
    text = text.replace('  ', ' ')

    url = WIKIFIER_ENDPOINT
    payload = json.dumps({
        "text": text,
        "threshold": WIKIFIER_THRESHOLD,
        "coref": True
    })
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
    except:
        return {}

    if response.status_code != 200:
        return {}

    return json.loads(response.text)


def call_restaurant_endpoint(endpoint: str, search_query: str, num_results: int, location_list: list) -> dict:
    url = endpoint
    payload = json.dumps({
        "query": search_query,
        "location_list": location_list,
        "num_results": num_results
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        return {}
    return json.loads(response.text)
