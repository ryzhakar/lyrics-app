from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .parser import LineBlock, ParsedSong


def build_chord_line(line: LineBlock, show_chords: bool) -> str:
    """Build a chord line preserving positions."""
    if not show_chords:
        return ''
    if not line.lyrics.strip() and any(line.chords):
        chord_tokens: list[str] = [ch or '' for ch in line.chords if ch]
        return ' '.join(chord_tokens)
    max_len = 0
    tokens: list[tuple[int, str]] = []
    for idx, ch in enumerate(line.chords):
        position = line.chord_positions[idx]
        token = ch or ''
        tokens.append((position, token))
        max_len = max(max_len, position + len(token))
    chars: list[str] = [' '] * max_len
    for position, token in tokens:
        for offset, character in enumerate(token):
            target_index = position + offset
            if target_index >= len(chars):
                chars.extend([' '] * (target_index + 1 - len(chars)))
            chars[target_index] = character
    return ''.join(chars)


def render_parsed_song(parsed: ParsedSong, show_chords: bool) -> str:
    """Render a parsed song into HTML with monospace alignment."""
    parts: list[str] = []
    for section in parsed.sections:
        parts.append('<section class="song-section">')
        if section.name:
            parts.append(f'<h3 class="section-header">{escape(section.name)}</h3>')
        for line in section.lines:
            chord_line = build_chord_line(line, show_chords)
            lyric_line = escape(line.lyrics)
            if chord_line:
                parts.append('<pre class="chords">' + escape(chord_line) + '</pre>')
            parts.append('<pre class="lyrics">' + lyric_line + '</pre>')
        parts.append('</section>')
    return ''.join(parts)
