from __future__ import annotations

from app.transposer import compute_semitone_interval, prefer_sharps_for_key, transpose_chord_symbol


def test_compute_semitone_interval_edge_cases() -> None:
    assert compute_semitone_interval(None, 'D') == 0
    assert compute_semitone_interval('C', None) == 0
    assert compute_semitone_interval('Db', 'C#') == 0


def test_transpose_chord_symbol_idempotent_zero() -> None:
    out = transpose_chord_symbol('F#m7b5', 0)
    assert out in {'F#m7b5', 'Gbm7b5'}


def test_prefer_sharps_major_circle_of_fifths() -> None:
    assert prefer_sharps_for_key('G') is True
    assert prefer_sharps_for_key('D') is True
    assert prefer_sharps_for_key('E') is True
    assert prefer_sharps_for_key('B') is True
    assert prefer_sharps_for_key('F#') is True
    assert prefer_sharps_for_key('C#') is True
    assert prefer_sharps_for_key('C') is False
    assert prefer_sharps_for_key('F') is False
    assert prefer_sharps_for_key('Bb') is False
    assert prefer_sharps_for_key('Eb') is False
    assert prefer_sharps_for_key('Ab') is False
    assert prefer_sharps_for_key('Db') is False
    assert prefer_sharps_for_key('Gb') is True
    assert prefer_sharps_for_key('Cb') is True


def test_prefer_sharps_minor_circle_of_fifths() -> None:
    assert prefer_sharps_for_key('Am') is True
    assert prefer_sharps_for_key('Em') is True
    assert prefer_sharps_for_key('Bm') is True
    assert prefer_sharps_for_key('F#m') is True
    assert prefer_sharps_for_key('C#m') is True
    assert prefer_sharps_for_key('G#m') is True
    assert prefer_sharps_for_key('D#m') is True
    assert prefer_sharps_for_key('A#m') is True
    assert prefer_sharps_for_key('Dm') is False
    assert prefer_sharps_for_key('Gm') is False
    assert prefer_sharps_for_key('Cm') is False
    assert prefer_sharps_for_key('Fm') is False
    assert prefer_sharps_for_key('Bbm') is False
    assert prefer_sharps_for_key('Ebm') is True
    assert prefer_sharps_for_key('Abm') is True
