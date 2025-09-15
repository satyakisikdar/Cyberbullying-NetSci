from src.pickle_sessions import build_session_graphs
from src.redo_count_motifs import find_and_insert_all_motifs


def main() -> None:
    build_session_graphs(snapshot_directory=None, is_true_graph=True)
    # find_and_insert_all_motifs()


if __name__ == "__main__":
    main()
