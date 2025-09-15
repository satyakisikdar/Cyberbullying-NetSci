# pyright: basic
import pytest
from src.graph_builder import GraphBuilder


def test_graph_builder(basic_graph, session_comments):
    builder = GraphBuilder(basic_graph)
    for author_role in session_comments:
        builder.add_node(author_role)
        if author_role.role != "main_victim":
            builder.add_edge(author_role)

    assert len(builder.current_bullies) == 2
    assert len(builder.current_victims) == 2
    assert len(builder.current_defenders) == 2

    assert basic_graph.num_nodes == 6
    assert basic_graph.num_edges == 10

    assert basic_graph.num_victims == 2
    assert basic_graph.num_bullies == 2
    assert basic_graph.num_defenders == 2
    assert basic_graph.num_non_agg_defenders == 1
    assert basic_graph.num_agg_defenders == 1
    assert basic_graph.num_non_agg_victims == 0
    assert basic_graph.num_agg_victims == 1

    assert basic_graph.main_victim_in_deg == 3
    assert basic_graph.main_victim_out_deg == 1

    assert basic_graph.victim_avg_in_deg == pytest.approx(3.0)
    assert basic_graph.victim_avg_out_deg == pytest.approx(1.0)

    assert basic_graph.bully_avg_in_deg == pytest.approx(1.0)
    assert basic_graph.bully_avg_out_deg == pytest.approx(2.0)
