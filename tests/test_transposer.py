from app.transposer import compute_semitone_interval, transpose_chord_symbol


def test_compute_semitone_interval_basic() -> None:
    assert compute_semitone_interval('C', 'D') == 2
    assert compute_semitone_interval('C', 'G') == 7


def test_transpose_chord_symbol_handles_slash() -> None:
    assert transpose_chord_symbol('D/F#', 2).startswith('E/')
