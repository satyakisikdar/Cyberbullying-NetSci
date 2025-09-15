# pyright: basic
import pickle
from datetime import datetime
from unittest.mock import Mock

import pytest
import numpy as np

from src.session_digraph import SessionDiGraph


def test_out_of_order_edge_placement(basic_graph):
    main_victim = Mock()
    main_victim.author_name = "main_victim"
    main_victim.role = "main_victim"
    main_victim.severity = 0.0
    main_victim.__hash__ = lambda s: hash(("main_victim", "main_victim"))

    bully_1 = Mock()
    bully_1.author_name = "bully_1"
    bully_1.role = "bully"
    bully_1.severity = 1.0
    bully_1.__hash__ = lambda s: hash(("bully_1", "bully"))
    with pytest.raises(ValueError):
        basic_graph.add_edge(bully_1, main_victim, weight=bully_1.severity)


def test_from_session(basic_session):
    """Test creating SessionDiGraph from Session object"""
    graph = SessionDiGraph.from_session(basic_session, is_true_graph=True)
    assert graph.unit_id == 123
    assert graph.owner_username == "test_owner"
    assert graph.owner_comment == "Test comment"
    assert graph.num_likes == 10
    assert graph.num_bullying_comments == 5
    assert graph.num_comments == 20
    assert graph.topic_vector.tolist() == [0, 2, 1, 0, 0, 3, 0, 0, 0, 1]
    assert graph.is_true_graph


def test_initialization():
    """Test proper initialization of SessionDiGraph"""
    graph = SessionDiGraph(
        unit_id=42,
        owner_username="test_user",
        owner_comment="Test comment",
        num_likes=100,
        num_bullying_comments=15,
        num_comments=50,
        topic_vector=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        is_true_graph=False,
    )

    assert graph.unit_id == 42
    assert graph.owner_username == "test_user"
    assert graph.owner_comment == "Test comment"
    assert graph.num_likes == 100
    assert graph.num_bullying_comments == 15
    assert graph.num_comments == 50
    assert isinstance(graph.topic_vector, np.ndarray)
    assert graph.topic_vector.tolist() == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert graph.is_true_graph is False


def test_most_frequent_topic(basic_graph):
    assert basic_graph.most_frequent_topic() == "Race"


def test_process_degrees_single_value(basic_graph):
    """Test _process_degrees with single value"""
    result = basic_graph._process_degrees(3.14)
    assert result == 3.14


def test_process_non_empty_list(basic_graph):
    """Test _process_degrees with iterable"""
    iter_values = [("node1", 2), ("node2", 4), ("node3", 6)]
    result = basic_graph._process_degrees(iter_values)
    assert result == 4.0  # mean of [2, 4, 6]


def test_process_degrees_empty_list(basic_graph):
    """Test _process_degrees with empty iterable"""
    result = basic_graph._process_degrees([])
    assert result == 0.0


def test_percent_comments_bullying(basic_graph):
    """Test percent_comments_bullying property"""
    assert basic_graph.percent_comments_bullying == 0.25


def test_percent_comments_bullying_with_zero_comments(basic_graph):
    """Test percent_comments_bullying property with zero comments"""
    basic_graph.num_comments = 0
    basic_graph.num_bullying_comments = 0
    with pytest.raises(ZeroDivisionError):
        _ = basic_graph.percent_comments_bullying


def test_num_properties(populated_graph):
    """Test various numerical properties"""
    assert populated_graph.num_nodes == 6
    assert populated_graph.num_edges == 8
    assert populated_graph.num_bullies == 2
    assert populated_graph.num_victims == 2
    assert populated_graph.num_non_agg_victims == 0
    assert populated_graph.num_agg_victims == 1
    assert populated_graph.num_defenders == 2
    assert populated_graph.num_non_agg_defenders == 1
    assert populated_graph.num_agg_defenders == 1


def test_main_victim_degrees(populated_graph):
    """Test main victim degree properties"""
    assert populated_graph.main_victim_in_deg == 3
    assert populated_graph.main_victim_out_deg == 0


def test_main_victim_weighted_degrees(populated_graph):
    """Test main victim degree properties"""
    assert populated_graph.main_victim_weighted_in_deg == pytest.approx(3.0)
    assert populated_graph.main_victim_weighted_out_deg == pytest.approx(0.0)


def test_victim_average_degrees(populated_graph):
    """Test victim average degree properties"""
    assert populated_graph.victim_avg_in_deg == pytest.approx(1.5)
    assert populated_graph.victim_avg_out_deg == pytest.approx(1.0)


def test_victim_score(populated_graph) -> None:
    assert populated_graph.victim_score == pytest.approx(-0.5)
    assert populated_graph.victim_score_weighted == pytest.approx(-0.5)


def test_bully_average_degrees(populated_graph):
    """Test bully average degree properties"""
    assert populated_graph.bully_avg_in_deg == pytest.approx(2.5)
    assert populated_graph.bully_avg_out_deg == pytest.approx(1.0)


def test_bully_average_weighted_degrees(populated_graph):
    """Test bully average degree properties"""
    assert populated_graph.bully_avg_weighted_in_deg == pytest.approx(3.0)
    assert populated_graph.bully_avg_weighted_out_deg == pytest.approx(1.0)


def test_bully_score(populated_graph):
    """Test various score properties"""
    assert populated_graph.bully_score == pytest.approx(-1.5)
    assert populated_graph.bully_score_weighted == pytest.approx(-2.0)


def test_add_edge_new_edge(basic_graph):
    """Test adding a new edge"""
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

    basic_graph.add_edge(bully_1, main_victim, weight=bully_1.severity)
    assert basic_graph.has_edge(
        bully_1,
        main_victim,
    )
    assert basic_graph[bully_1][main_victim]["weight"] == 1.0


def test_add_edge_existing_edge(basic_graph):
    """Test adding weight to existing edge"""
    main_victim = Mock()
    main_victim.author_name = "main_victim"
    main_victim.role = "main_victim"
    main_victim.severity = 0.0
    main_victim.__hash__ = lambda s: hash(("main_victim", "main_victim"))
    basic_graph.add_node(main_victim, type=main_victim.role, layer=0.0)

    bully_1 = Mock()
    bully_1.author_name = "bully_1"
    bully_1.role = "bully"
    bully_1.severity = 2.0
    bully_1.__hash__ = lambda s: hash(("bully_1", "bully"))

    basic_graph.add_node(bully_1, type=bully_1.role, layer=0.0)
    basic_graph.add_edge(bully_1, main_victim, weight=bully_1.severity)
    basic_graph.add_edge(bully_1, main_victim, weight=bully_1.severity)

    assert basic_graph[bully_1][main_victim]["weight"] == 4.0
    assert basic_graph.number_of_edges() == 1


def test_empty_graph_properties(basic_graph):
    """Test properties on empty graph"""
    main_victim = Mock()
    main_victim.role = "main_victim"
    basic_graph.add_node(main_victim, type=main_victim.role, layer=0.0)
    assert basic_graph.num_nodes == 1
    assert basic_graph.num_edges == 0
    assert basic_graph.main_victim_in_deg == 0
    assert basic_graph.main_victim_out_deg == 0


def test_graph_with_no_victims_or_bullies(basic_graph):
    """Test graph with only neutral nodes"""
    assert len(basic_graph.victims) == 0
    assert len(basic_graph.bullies) == 0
    assert basic_graph.victim_avg_in_deg == 0.0
    assert basic_graph.bully_avg_in_deg == 0.0
