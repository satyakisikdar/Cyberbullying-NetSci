import igraph as ig

from src.motif_graph import MotifGraph
from src.count_motifs import (
    compute_motifs_randesu,
    transform_motifies,
    process_motifies,
)


def test_compute_motifs_randesu_size_3(populated_graph_motif_count_size_3):
    """Test basic motif finding for graphs of size 3"""
    session_igraph = ig.Graph.from_networkx(populated_graph_motif_count_size_3)

    motifs = compute_motifs_randesu(session_igraph, size=3)
    iso_classes = len(motifs)
    assert iso_classes == 1
    for iso_class, vertex_lists in motifs.items():
        for vertices in vertex_lists:
            assert len(vertices) == 3
        assert len(vertex_lists) == 1


def test_compute_motifs_randesu_size_4(populated_graph_motif_count_size_4):
    """Test basic motif finding for graphs of size 4"""
    session_igraph = ig.Graph.from_networkx(populated_graph_motif_count_size_4)

    motifs = compute_motifs_randesu(session_igraph, size=4)
    iso_classes = len(motifs)
    assert iso_classes == 1
    for iso_class, vertex_lists in motifs.items():
        for vertices in vertex_lists:
            assert len(vertices) == 4
            assert len(vertex_lists) == 1


def test_transform_motifies_size_3(populated_graph_motif_count_size_3):
    """Test motif transformation for graphs of size 3"""
    session_igraph = ig.Graph.from_networkx(populated_graph_motif_count_size_3)

    test_vertices = (0, 1, 2)
    transformed = transform_motifies(
        session_igraph, test_vertices, node_flavor="fine", edge_flavor="fine"
    )
    assert "mapped_type" in transformed.vs.attributes()
    assert "binned_weight" in transformed.es.attributes()

    for mapped_type in transformed.vs["mapped_type"]:
        assert mapped_type in [0, 5]

    for binned_weight in transformed.es["binned_weight"]:
        assert binned_weight > 0


def test_transform_motifies_size_4(populated_graph_motif_count_size_4):
    """Test motif transformation for graphs of size 3"""
    session_igraph = ig.Graph.from_networkx(populated_graph_motif_count_size_4)

    test_vertices = (0, 1, 2, 3)
    transformed = transform_motifies(
        session_igraph, test_vertices, node_flavor="fine", edge_flavor="fine"
    )
    assert "mapped_type" in transformed.vs.attributes()
    assert "binned_weight" in transformed.es.attributes()

    for mapped_type in transformed.vs["mapped_type"]:
        assert mapped_type in [0, 5]

    for binned_weight in transformed.es["binned_weight"]:
        assert binned_weight > 0


def test_process_motifies_size_3(populated_graph_motif_count_size_3):
    """Test motif processing for graphs of size 3"""
    session_igraph = ig.Graph.from_networkx(populated_graph_motif_count_size_3)
    unit_id = 123
    motifs_vertices = {
        0: [(0, 1, 2)],
    }
    SIZE = 4
    result = process_motifies(
        unit_id,
        session_igraph,
        motifs_vertices,
        node_flavor="fine",
        edge_flavor="fine",
        size=SIZE,
    )
    assert isinstance(result, list)
    assert len(result) == 1
    for motif in result:
        assert isinstance(motif, MotifGraph)
        assert motif.unit_id == unit_id
        assert motif.node_flavor == "fine"
        assert motif.edge_flavor == "fine"
        assert motif.count == 1


def test_process_motifies_size_4(populated_graph_motif_count_size_4):
    """Test motif processing for graphs of size 4"""
    session_igraph = ig.Graph.from_networkx(populated_graph_motif_count_size_4)
    unit_id = 123
    motifs_vertices = {
        0: [(0, 1, 2, 3)],
    }
    SIZE = 4
    result = process_motifies(
        unit_id,
        session_igraph,
        motifs_vertices,
        node_flavor="fine",
        edge_flavor="fine",
        size=SIZE,
    )
    assert isinstance(result, list)
    assert len(result) == 1
    for motif in result:
        assert isinstance(motif, MotifGraph)
        assert motif.unit_id == unit_id
        assert motif.node_flavor == "fine"
        assert motif.edge_flavor == "fine"
        assert motif.count == 1
