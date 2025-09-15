# pyright: basic
from datetime import datetime
from unittest.mock import Mock

import pytest

from src.session import Session
from src.session_digraph import SessionDiGraph


@pytest.fixture
def session_comments():
    main_victim = Mock()
    main_victim.author_name = "main_victim"
    main_victim.role = "main_victim"
    main_victim.severity = 0.0
    main_victim.__hash__ = lambda s: hash(("main_victim", "main_victim"))

    agg_victim_1 = Mock()
    agg_victim_1.author_name = "agg_victim_1"
    agg_victim_1.role = "aggressive_victim"
    agg_victim_1.severity = 1.0
    agg_victim_1.__hash__ = lambda s: hash(("agg_victim_1", "aggressive_victim"))

    bully_1 = Mock()
    bully_1.author_name = "bully_1"
    bully_1.role = "bully"
    bully_1.severity = 1.0
    bully_1.__hash__ = lambda s: hash(("bully_1", "bully"))

    bully_2 = Mock()
    bully_2.author_name = "bully_2"
    bully_2.role = "bully"
    bully_2.severity = 1.0
    bully_2.__hash__ = lambda s: hash(("bully_2", "bully"))

    non_agg_defender_1 = Mock()
    non_agg_defender_1.author_name = "non_agg_defender_1"
    non_agg_defender_1.role = "non_aggressive_defender:support_of_the_victim"
    non_agg_defender_1.severity = 1.0
    non_agg_defender_1.__hash__ = lambda s: hash(
        ("non_agg_defender_1", "non_aggressive_defender:support_of_the_victim")
    )

    agg_defender_1 = Mock()
    agg_defender_1.author_name = "agg_defender_1"
    agg_defender_1.role = "aggressive_defender"
    agg_defender_1.severity = 1.0
    agg_defender_1.__hash__ = lambda s: hash(("agg_defender_1", "aggressive_defender"))
    comments = [
        main_victim,
        agg_victim_1,
        bully_1,
        bully_2,
        non_agg_defender_1,
        agg_defender_1,
    ]
    return comments


@pytest.fixture
def basic_session() -> Session:
    session = Session(
        unit_id=123,
        posted_at=datetime.now(),
        owner_user_name="test_owner",
        owner_comment="Test comment",
        main_victim="OP",
        num_likes=10,
        num_bullying_comments=5,
        num_comments=20,
        topic_vector=[0, 2, 1, 0, 0, 3, 0, 0, 0, 1],
    )
    return session


@pytest.fixture
def basic_graph(basic_session) -> SessionDiGraph:
    """Create a basic SessionDiGraph for testing"""
    graph = SessionDiGraph.from_session(basic_session, is_true_graph=True)
    return graph


@pytest.fixture
def populated_graph(basic_graph):
    """Create a populated graph with various node types and edges"""

    main_victim = Mock()
    main_victim.author_name = "main_victim"
    main_victim.role = "main_victim"
    main_victim.severity = 0.0
    main_victim.__hash__ = lambda s: hash(("main_victim", "main_victim"))
    basic_graph.add_node(main_victim, type=main_victim.role, layer=0.0)

    agg_victim_1 = Mock()
    agg_victim_1.author_name = "agg_victim_1"
    agg_victim_1.role = "aggressive_victim"
    agg_victim_1.severity = 1.0
    agg_victim_1.__hash__ = lambda s: hash(("agg_victim_1", "aggressive_victim"))
    basic_graph.add_node(agg_victim_1, type=agg_victim_1.role, layer=0.0)

    bully_1 = Mock()
    bully_1.author_name = "bully_1"
    bully_1.role = "bully"
    bully_1.severity = 1.0
    bully_1.__hash__ = lambda s: hash(("bully_1", "bully"))
    basic_graph.add_node(bully_1, type=bully_1.role, layer=0.0)

    bully_2 = Mock()
    bully_2.author_name = "bully_2"
    bully_2.role = "bully"
    bully_2.severity = 1.0
    bully_2.__hash__ = lambda s: hash(("bully_2", "bully"))
    basic_graph.add_node(bully_2, type=bully_2.role, layer=0.0)

    non_agg_defender_1 = Mock()
    non_agg_defender_1.author_name = "non_agg_defender_1"
    non_agg_defender_1.role = "non_aggressive_defender:support_of_the_victim"
    non_agg_defender_1.severity = 1.0
    non_agg_defender_1.__hash__ = lambda s: hash(
        ("non_agg_defender_1", "non_aggressive_defender:support_of_the_victim")
    )
    basic_graph.add_node(non_agg_defender_1, type=non_agg_defender_1.role, layer=0.0)

    agg_defender_1 = Mock()
    agg_defender_1.author_name = "agg_defender_1"
    agg_defender_1.role = "aggressive_defender"
    agg_defender_1.severity = 2.0
    agg_defender_1.__hash__ = lambda s: hash(("agg_defender_1", "aggressive_defender"))
    basic_graph.add_node(agg_defender_1, type=agg_defender_1.role, layer=0.0)

    basic_graph.add_edge(bully_1, main_victim, weight=bully_1.severity)
    basic_graph.add_edge(bully_2, main_victim, weight=bully_2.severity)
    basic_graph.add_edge(
        non_agg_defender_1, bully_1, weight=non_agg_defender_1.severity
    )
    basic_graph.add_edge(
        non_agg_defender_1, bully_2, weight=non_agg_defender_1.severity
    )
    basic_graph.add_edge(
        non_agg_defender_1, main_victim, weight=non_agg_defender_1.severity
    )
    basic_graph.add_edge(agg_victim_1, bully_1, weight=agg_victim_1.severity)
    basic_graph.add_edge(agg_victim_1, bully_2, weight=agg_victim_1.severity)
    basic_graph.add_edge(agg_defender_1, bully_1, weight=agg_defender_1.severity)

    return basic_graph


@pytest.fixture
def populated_graph_motif_count_size_3(basic_graph):
    main_victim = Mock()
    main_victim.author_name = "main_victim"
    main_victim.role = "main_victim"
    main_victim.severity = 0.0
    main_victim.__hash__ = lambda s: hash(("main_victim", "main_victim"))
    basic_graph.add_node(main_victim, type=main_victim.role, layer=0.0)
    bully_1 = Mock()
    bully_1.author_name = "bully_1"
    bully_1.role = "bully"
    bully_1.severity = 1.0
    bully_1.__hash__ = lambda s: hash(("bully_1", "bully"))
    basic_graph.add_node(bully_1, type=bully_1.role, layer=0.0)

    bully_2 = Mock()
    bully_2.author_name = "bully_2"
    bully_2.role = "bully"
    bully_2.severity = 1.0
    bully_2.__hash__ = lambda s: hash(("bully_2", "bully"))
    basic_graph.add_node(bully_2, type=bully_2.role, layer=0.0)

    basic_graph.add_edge(bully_1, main_victim, weight=bully_1.severity)
    basic_graph.add_edge(bully_2, main_victim, weight=bully_2.severity)

    return basic_graph


@pytest.fixture
def populated_graph_motif_count_size_4(basic_graph):
    main_victim = Mock()
    main_victim.author_name = "main_victim"
    main_victim.role = "main_victim"
    main_victim.severity = 0.0
    main_victim.__hash__ = lambda s: hash(("main_victim", "main_victim"))
    basic_graph.add_node(main_victim, type=main_victim.role, layer=0.0)
    bully_1 = Mock()
    bully_1.author_name = "bully_1"
    bully_1.role = "bully"
    bully_1.severity = 1.0
    bully_1.__hash__ = lambda s: hash(("bully_1", "bully"))
    basic_graph.add_node(bully_1, type=bully_1.role, layer=0.0)

    bully_2 = Mock()
    bully_2.author_name = "bully_2"
    bully_2.role = "bully"
    bully_2.severity = 1.0
    bully_2.__hash__ = lambda s: hash(("bully_2", "bully"))
    basic_graph.add_node(bully_2, type=bully_2.role, layer=0.0)

    bully_3 = Mock()
    bully_3.author_name = "bully_3"
    bully_3.role = "bully"
    bully_3.severity = 1.0
    bully_3.__hash__ = lambda s: hash(("bully_3", "bully"))
    basic_graph.add_node(bully_3, type=bully_3.role, layer=0.0)

    basic_graph.add_edge(bully_1, main_victim, weight=bully_1.severity)
    basic_graph.add_edge(bully_2, main_victim, weight=bully_2.severity)
    basic_graph.add_edge(bully_3, main_victim, weight=bully_3.severity)

    return basic_graph
