import streamlit as st
from src.const import *
from src.search_engine import (process_qa, process_search, restaurant_search)
from src.utils import (get_query_type, is_bonus_query, is_tds_qa, select_root_and_get_cards_list, select_card_to_open)
from streamlit_agraph import (Config, Edge, Node, agraph)

# App title
st.title("Search")


def prepare_layout():
    st.sidebar.markdown("### Semantic search engine")
    st.sidebar.markdown("This search engine is built by training language models on articles from "
                        "[Towards Data Science](https://towardsdatascience.com/). It contains all the articles "
                        "from 2020 to 2021.")
    st.sidebar.markdown('#### Instructions:')
    instructions = """
    1. Type a query in natural language:
        * I need a good article that explains how to train a T5 transformers with code examples
    2. Explore card collections with the command *explore*:
        * explore: how to
    3. Open cards with the command *open*:
        * open: 1
    """
    st.sidebar.markdown(instructions)
    st.sidebar.markdown('You can also ask questions, for example:')
    st.sidebar.markdown('   * *What does it take to be a data scientist?*')
    st.sidebar.markdown(' ')
    with st.sidebar.expander('Want more?'):
        st.write("The search engine is trained on scientific articles but it can be generalized "
                 "to any type of content on the internet, for example, restaurants reviews.")
        res_instructions = """
        1. Try searching for a restaurant by describing what you are looking for
            * res: I want a place where I can talk to friends and have some good drinks
        2. Explore card collections with the command *res-explore*:
            * res-explore: American (New)
            
        Remember to use the prefix 'res' on your queries!
        """
        st.markdown(res_instructions)


def process_tds_search(query: str):
    root_cards_list = process_search(search_query=query, search_engine_type=TDSSearchEngineType.MIX,
                                     num_results_to_retrieve=TDS_NUM_RESULTS)
    if not root_cards_list:
        st.error("Something went wrong with the search engine :(")
        return

    # Cache the current global state
    st.session_state.root_cards_list = root_cards_list

    # Print number of results
    num_results = 0
    for root_card in root_cards_list:
        num_results += root_card.get_num_children()
    st.markdown("##### Found " + str(num_results) + " results")

    # Print root cards
    for root_card in root_cards_list:
        st.markdown("***")

        # Card type
        st.markdown("### " + root_card.card_type.title())
        st.markdown("Collection type: " + root_card.card_type)

        # Number of children
        num_cards = root_card.get_num_children()
        st.markdown(str(num_cards) + " result" + "s" if num_cards > 1 else "")

        # Top ranked results
        st.markdown("Top ranked result:")
        st.markdown("[" + root_card.top_ranked_result_title + '](' + root_card.top_ranked_result_url + ')')


def process_restaurant_search(query: str):
    root_cards_list = restaurant_search(search_query=query, num_results_to_retrieve=RESTAURANT_NUM_RESULTS)
    if not root_cards_list:
        st.error("Something went wrong with the search engine :(")
        return

    # Cache the current global state
    st.session_state.res_root_cards_list = root_cards_list

    # Print number of results
    num_results = 0
    for root_card in root_cards_list:
        num_results += root_card.get_num_children()
    st.markdown("##### Found " + str(num_results) + " results")

    # Print root cards
    for root_card in root_cards_list:
        st.markdown("***")

        # Card type
        st.markdown("### " + root_card.card_type.title())

        # Number of children
        num_cards = root_card.get_num_children()
        st.markdown(str(num_cards) + " result" + "s" if num_cards > 1 else "")

        # Top ranked results
        st.markdown("Top ranked result:")

        # Score
        st.markdown("Score: " + str(root_card.top_ranked_score))

        # Preview of review matching the query
        st.markdown("[" + root_card.top_ranked_result_name + '](' + root_card.top_ranked_result_url + ')')
        st.write(root_card.top_ranked_review[:150] + "...")


def process_tds_qa(query: str):
    with st.spinner('Processing...'):
        # QA takes some time to process, tell the user
        answer_list = process_qa(search_query=query, num_results_to_retrieve=TDS_QA_NUM_RESULTS,
                                 num_results_reader=TDS_QA_NUM_READER)
        if not answer_list:
            st.error("Something went wrong with the search engine :(")
            return

        # Print answer, score, and the article the answer was taken from
        st.markdown("***" + answer_list[0]["answer"] + "***")
        st.markdown("Score: " + str(answer_list[0]["score"]))
        st.markdown("Article: [" + answer_list[0]["card"]["title"] + '](' + answer_list[0]["card"]["url"] + ')')
        with st.expander("Summary"):
            st.write(answer_list[0]["card"]["summary"])

        # Print other possible answers
        if len(answer_list) > 1:
            with st.expander("Similar results"):
                for idx, ans in enumerate(answer_list):
                    if idx == 0:
                        continue
                    st.markdown("***")
                    st.markdown(answer_list[idx]["answer"])
                    st.markdown("Score: " + str(answer_list[idx]["score"]))
                    st.markdown("Article: [" + answer_list[0]["card"]["title"] + '](' + answer_list[0]["card"]["url"] + ')')


def add_card_related_concepts(card):
    # Build the graph to visualize
    nodes = list()
    edges = list()

    # Current node
    target_id = card.get_parent().card_type
    nodes.append(Node(id=target_id, size=400))

    # Parent node
    parent_id = "Query: " + card.search_query
    nodes.append(Node(id=parent_id, size=400, symbolType='square'))

    # Connect parent to current node
    edges.append(Edge(source=parent_id,
                      label="result",
                      target=target_id,
                      type="STRAIGHT")
                 )

    # Connect all concepts to the Root card
    for entity in card.related_concepts:
        nodes.append(Node(id=entity["title"], size=400))
        edges.append(Edge(source=target_id,
                          # label="relates",
                          target=entity["title"],
                          type="CURVE_SMOOTH")
                     )

    # Build the graph
    config = Config(width=700,
                    height=500,
                    directed=True,
                    nodeHighlightBehavior=True,
                    highlightColor="#F7A7A6",  # or "blue"
                    collapsible=False,
                    node={'labelProperty': 'label'},
                    link={'labelProperty': 'label', 'renderLabel': True},
                    node_color="blue"
                    # **kwargs e.g. node_size=1000 or node_color="blue"
                    )

    # Visualize the graph
    with st.expander("Related concepts"):
        return_value = agraph(nodes=nodes, edges=edges, config=config)

        st.markdown("###### Concepts:")
        for entity in card.related_concepts:
            st.markdown("[" + entity["title"] + "](" + entity["url"] + ")")


def handle_invalid_query():
    """
    Handles an invalid user query.
    :return: None
    """
    st.error("Invalid or not supported query. Try changing your query.")


# ------- Restaurant ------ #


def handle_restaurant_query(query: str):
    """
    Handles the bonus 'restaurant' queries.
    :param query: the restaurant query.
    :return: None
    """
    query = query[len("res:"):].strip()
    process_restaurant_search(query)


def handle_explore_restaurant_query(query: str):
    """
    Handles an Explore Restaurant Root Card query.
    :param query: the query.
    :return: None
    """
    if "res_root_cards_list" not in st.session_state:
        st.error("No Cards to explore, have you typed a query?")
        return

    # Get the current list of root Cards
    root_cards_list = st.session_state.res_root_cards_list

    # Get the root selected by the user
    cards_list = select_root_and_get_cards_list(query, root_cards_list)
    if cards_list is None:
        st.error("Something went wrong while opening Cards :(")
        return

    # Process each Card
    for idx, card in enumerate(cards_list):
        st.markdown("***")

        # Card title
        st.markdown('##### ' + card.card_meta["name"])

        # Card info
        st.markdown("[" + card.info["url"][:40] + "...](" + card.info["url"] + ")")
        st.markdown("Rating: " + str(card.info["rating"]))
        st.markdown("Price: " + str(card.info["price"]))
        st.markdown("Location: " + card.info["city"])

        # Other information
        with st.expander("More info"):
            st.markdown("Reviews: " + str(card.info["num_reviews"]))
            categories = card.info["categories"]
            st.markdown("Restaurant type: " + ', '.join(categories))

        # Context
        with st.expander("Context"):
            st.markdown("**Query**: " + card.search_query)
            st.write(card.context)


def handle_open_restaurant_query(query: str):
    """
    Handles res-open: type queries.
    :return: None
    """
    st.error("Opening Cards for restaurants is not yet possible :(")


# ------- TDS ------ #


def handle_tds_query(query: str):
    """
    Handles a standard TDS query.
    A TDS query can be a question/answer query or a
    search for some articles type of query.
    :param query: the TDS query.
    :return: None
    """
    if is_tds_qa(query):
        # Answer query first
        process_tds_qa(query)

    # Process standard TDS query
    process_tds_search(query)


def handle_explore_query(query: str):
    """
    Handles an Explore Root TDS Card query.
    :param query: the query.
    :return: None
    """
    if "root_cards_list" not in st.session_state:
        st.error("No Cards to explore, have you typed a query?")
        return

    # Get the current list of root Cards
    root_cards_list = st.session_state.root_cards_list

    # Get the root selected by the user
    cards_list = select_root_and_get_cards_list(query, root_cards_list)
    if cards_list is None:
        st.error("Something went wrong while opening Cards :(")
        return

    # Cache the current list of Cards in the global state
    st.session_state.cards_list = cards_list

    # Process each Card
    for idx, card in enumerate(cards_list):
        st.markdown("***")

        # Card title and index
        st.markdown('##### ' + card.card_data["title"])
        st.markdown("###### Index: " + str(idx))

        # Add 2 columns: Card image |  Card MetaData
        col1, col2 = st.columns(2)
        with col1:
            image_url = card.image
            st.image(
                image_url,
                width=200,
            )
        with col2:
            st.markdown("[" + card.card_data["url"][:40] + "...](" + card.card_data["url"] + ")")
            st.markdown("Votes: " + str(card.card_data["num_votes"]))
            st.markdown("About: " + card.card_data["concept"])
            st.markdown('Date: ' + card.card_data["date"])
            card_topics = card.card_data["topics"]
            if card_topics:
                topics_list = list()
                for topic in card_topics:
                    topics_list.append(topic['topic'])
                st.markdown("Keywords: " + ', '.join(topics_list))

        # Article summary
        with st.expander("Summary"):
            st.write(card.card_data["summary"])


def handle_open_query(query: str):
    """
    Handles an Open Card query.
    :param query: the query.
    :return: None
    """
    if "cards_list" not in st.session_state:
        st.error("No Cards to open, are you exploring a root Card?")
        return
    cards_list = st.session_state.cards_list

    # Get the Card to open and open it
    card = select_card_to_open(query, cards_list)

    # Print the Card
    st.markdown("***")
    st.markdown("[" + card.card_data["url"][:40] + "...](" + card.card_data["url"] + ")")
    st.markdown("#### " + card.card_data["title"])

    # Summary and about
    st.write(card.card_data["summary"].replace('. ', '.\n'))
    st.markdown("**About**: " + card.card_data["concept"])

    # Card MetaData
    with st.expander("MetaData"):
        col1, col2 = st.columns(2)
        with col1:
            image_url = card.image
            st.image(
                image_url,
                width=250,
            )
        with col2:
            st.markdown('Type: ' + card.get_parent().card_type)
            st.markdown('Score: ' + str(card.score))
            st.markdown('Date: ' + card.card_data["date"])
            st.markdown('Has code: ' + card.card_data["meta"]["code"])
            st.markdown('Length: ' + card.card_data["meta"]["length"])
            st.markdown('Votes: ' + str(card.card_data["num_votes"]))
            st.markdown('Responses: ' + str(card.card_data["num_responses"]))

    # Tag this Card
    with st.expander("Topics and Tags"):
        topics = card.card_data["topics"]
        tags_rank = card.card_data["tags_rank"]

        topics_list = list()
        for topic in topics:
            topics_list.append(topic['topic'])
        if topics_list:
            st.markdown("Topics: " + ', '.join(topics_list))

        tags_list = list()
        for tag_rank in tags_rank:
            tags_list.append(tag_rank["word"])
        if tags_list:
            st.markdown("Tags: " + ', '.join(tags_list))

    # Related concepts
    add_card_related_concepts(card)


def run():
    # Get search query
    input_query = st.text_input("", key="query")
    input_query = input_query.strip()

    # Switch action based on query
    query_type = get_query_type(input_query)
    if query_type is QueryType.EMPTY_QUERY:
        # Nothing to do
        pass
    elif query_type is QueryType.INVALID_QUERY:
        # Invalid query handling
        handle_invalid_query()
    elif query_type is QueryType.SEARCH_QUERY:
        handle_tds_query(input_query)
    elif query_type is QueryType.EXPLORE_QUERY:
        handle_explore_query(input_query)
    elif query_type is QueryType.OPEN_QUERY:
        handle_open_query(input_query)
    elif query_type is QueryType.RES_SEARCH_QUERY:
        handle_restaurant_query(input_query)
    elif query_type is QueryType.RES_EXPLORE_QUERY:
        handle_explore_restaurant_query(input_query)
    elif query_type is QueryType.RES_OPEN_QUERY:
        handle_open_restaurant_query(input_query)
    else:
        handle_invalid_query()


if __name__ == "__main__":
    # Prepare layout
    prepare_layout()

    # Run the app
    run()
