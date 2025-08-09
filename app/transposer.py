from __future__ import annotations

import re

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


def _normalize_key_to_root(key: str) -> str:
    """Normalize key token to root note used for intervals."""
    return key.rstrip('m')


def compute_semitone_interval(from_key: str | None, to_key: str | None) -> int:
    """Compute semitone interval between keys."""
    if not from_key or not to_key:
        return 0
    # mypy: after the guard above, values are non-None
    from_root: str = _normalize_key_to_root(from_key)
    to_root: str = _normalize_key_to_root(to_key)
    a = NOTE_TO_SEMITONE.get(from_root)
    b = NOTE_TO_SEMITONE.get(to_root)
    if a is None or b is None:
        return 0
    return (b - a) % 12


SHARP_KEYS = {'C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#'}
FLAT_KEYS = {'F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb'}


def prefer_sharps_for_key(key: str | None) -> bool:
    """Choose accidental style based on key."""
    if not key:
        return True
    root = key.rstrip('m')
    if root in SHARP_KEYS:
        return True
    return root not in FLAT_KEYS


def _respell_note(note: str, prefer_sharps: bool) -> str:
    """Respell a single note name to sharps or flats."""
    if prefer_sharps:
        return {
            'Db': 'C#',
            'Eb': 'D#',
            'Gb': 'F#',
            'Ab': 'G#',
            'Bb': 'A#',
        }.get(note, note)
    return {
        'C#': 'Db',
        'D#': 'Eb',
        'F#': 'Gb',
        'G#': 'Ab',
        'A#': 'Bb',
    }.get(note, note)


_ROOT_RE = re.compile(r'^([A-G](?:#|b)?)(.*)$')


def _respell_symbol_once(symbol: str, prefer_sharps: bool) -> str:
    """Respell a single chord symbol without slash bass."""
    m = _ROOT_RE.match(symbol)
    if not m:
        return symbol
    root, tail = m.group(1), m.group(2)
    return f'{_respell_note(root, prefer_sharps)}{tail}'


def respell_chord_symbol(symbol: str, prefer_sharps: bool) -> str:
    """Respell chord roots and bass to preferred accidentals."""
    if '/' in symbol:
        main, bass = symbol.split('/', 1)
        main_r = _respell_symbol_once(main, prefer_sharps)
        bass_r = _respell_symbol_once(bass, prefer_sharps)
        return f'{main_r}/{bass_r}'
    return _respell_symbol_once(symbol, prefer_sharps)


def transpose_chord_symbol(
    symbol: str,
    semitone_interval: int,
    prefer_sharps: bool | None = None,
) -> str:
    """Transpose a chord symbol by a semitone interval."""
    pref = True if prefer_sharps is None else prefer_sharps
    if '/' in symbol:
        main, bass = symbol.split('/', 1)
        main_t = Chord(main)
        bass_t = Chord(bass)
        main_t.transpose(semitone_interval)
        bass_t.transpose(semitone_interval)
        return respell_chord_symbol(f'{main_t}/{bass_t}', pref)
    chord = Chord(symbol)
    chord.transpose(semitone_interval)
    return respell_chord_symbol(str(chord), pref)
