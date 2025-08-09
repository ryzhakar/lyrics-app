from __future__ import annotations

from app.transposer import compute_semitone_interval, transpose_chord_symbol


def test_compute_semitone_interval_edge_cases() -> None:
    assert compute_semitone_interval(None, 'D') == 0
    assert compute_semitone_interval('C', None) == 0
    assert compute_semitone_interval('Db', 'C#') == 0


def test_transpose_chord_symbol_idempotent_zero() -> None:
    out = transpose_chord_symbol('F#m7b5', 0)
    assert out in {'F#m7b5', 'Gbm7b5'}
