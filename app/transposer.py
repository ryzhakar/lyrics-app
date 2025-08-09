from __future__ import annotations

from pychord import Chord  # type: ignore[import-not-found]

NOTE_TO_SEMITONE = {
    'C': 0,
    'C#': 1,
    'Db': 1,
    'D': 2,
    'D#': 3,
    'Eb': 3,
    'E': 4,
    'F': 5,
    'F#': 6,
    'Gb': 6,
    'G': 7,
    'G#': 8,
    'Ab': 8,
    'A': 9,
    'A#': 10,
    'Bb': 10,
    'B': 11,
}


def compute_semitone_interval(from_key: str | None, to_key: str | None) -> int:
    """Compute semitone interval between keys."""
    if not from_key or not to_key:
        return 0
    a = NOTE_TO_SEMITONE.get(from_key)
    b = NOTE_TO_SEMITONE.get(to_key)
    if a is None or b is None:
        return 0
    return (b - a) % 12


def transpose_chord_symbol(symbol: str, semitone_interval: int) -> str:
    """Transpose a chord symbol by a semitone interval."""
    if '/' in symbol:
        main, bass = symbol.split('/', 1)
        main_t = Chord(main)
        bass_t = Chord(bass)
        main_t.transpose(semitone_interval)
        bass_t.transpose(semitone_interval)
        return f'{main_t}/{bass_t}'
    chord = Chord(symbol)
    chord.transpose(semitone_interval)
    return str(chord)
