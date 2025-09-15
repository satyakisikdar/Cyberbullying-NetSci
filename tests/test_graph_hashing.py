# pyright: basic
import pytest
import igraph as ig
import networkx as nx
from typing import cast
from src.graph_hashing import weisfeiler_lehman_graph_hash


@pytest.fixture
def prepare_graphs():
    G1 = nx.DiGraph()
    G1.add_edges_from(
        [
            (1, 2, {"label": "A"}),
            (2, 3, {"label": "A"}),
            (3, 1, {"label": "A"}),
            (1, 4, {"label": "B"}),
        ]
    )
    nx.set_node_attributes(G1, name="_name", values={1: "A", 2: "B", 3: "C", 4: "D"})
    G2 = nx.DiGraph()
    G2.add_edges_from(
        [
            (5, 6, {"label": "B"}),
            (6, 7, {"label": "A"}),
            (7, 5, {"label": "A"}),
            (7, 8, {"label": "A"}),
        ]
    )
    nx.set_node_attributes(G2, name="_name", values={5: "W", 6: "X", 7: "Y", 8: "Z"})
    return G1, G2


def test_nx_vanillia(prepare_graphs) -> None:
    G1, G2 = prepare_graphs
    assert nx.weisfeiler_lehman_graph_hash(G1) == nx.weisfeiler_lehman_graph_hash(G2)


def test_nx_node_attr(prepare_graphs: tuple[nx.DiGraph, nx.DiGraph]) -> None:
    G1, G2 = prepare_graphs
    assert nx.weisfeiler_lehman_graph_hash(
        G1, node_attr="_name"
    ) != nx.weisfeiler_lehman_graph_hash(G2, node_attr="_name")


def test_nx_edge_attr(prepare_graphs: tuple[nx.DiGraph, nx.DiGraph]) -> None:
    G1, G2 = prepare_graphs
    assert nx.weisfeiler_lehman_graph_hash(
        G1, edge_attr="label"
    ) != nx.weisfeiler_lehman_graph_hash(G2, edge_attr="label")


def test_nx_node_and_edge_attr(
    prepare_graphs: tuple[nx.DiGraph, nx.DiGraph],
) -> None:
    G1, G2 = prepare_graphs
    assert nx.weisfeiler_lehman_graph_hash(
        G1, node_attr="_name", edge_attr="label"
    ) != nx.weisfeiler_lehman_graph_hash(G2, node_attr="_name", edge_attr="label")


def test_igraph_vanillia(prepare_graphs: tuple[nx.DiGraph, nx.DiGraph]) -> None:
    G1, G2 = prepare_graphs
    ig_G1 = cast(ig.Graph, ig.Graph.from_networkx(G1))
    ig_G2 = cast(ig.Graph, ig.Graph.from_networkx(G2))
    assert weisfeiler_lehman_graph_hash(ig_G1) == weisfeiler_lehman_graph_hash(ig_G2)


def test_igraph_node_attr(
    prepare_graphs: tuple[nx.DiGraph, nx.DiGraph],
) -> None:
    G1, G2 = prepare_graphs
    ig_G1 = ig.Graph.from_networkx(G1)
    ig_G2 = ig.Graph.from_networkx(G2)
    assert weisfeiler_lehman_graph_hash(
        ig_G1, node_attr="_name"
    ) != weisfeiler_lehman_graph_hash(ig_G2, node_attr="_name")


def test_igraph_edge_attr(
    prepare_graphs: tuple[nx.DiGraph, nx.DiGraph],
) -> None:
    G1, G2 = prepare_graphs
    ig_G1 = ig.Graph.from_networkx(G1)
    ig_G2 = ig.Graph.from_networkx(G2)
    assert weisfeiler_lehman_graph_hash(
        ig_G1, edge_attr="label"
    ) != weisfeiler_lehman_graph_hash(ig_G2, edge_attr="label")


def test_igraph_node_and_edge_attr(
    prepare_graphs: tuple[nx.DiGraph, nx.DiGraph],
) -> None:
    G1, G2 = prepare_graphs
    ig_G1 = ig.Graph.from_networkx(G1)
    ig_G2 = ig.Graph.from_networkx(G2)
    assert weisfeiler_lehman_graph_hash(
        ig_G1, node_attr="_name", edge_attr="label"
    ) != weisfeiler_lehman_graph_hash(ig_G2, node_attr="_name", edge_attr="label")
