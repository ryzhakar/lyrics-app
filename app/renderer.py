from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .parser import LineBlock, ParsedSong


def build_chord_line(line: LineBlock, show_chords: bool) -> str:
    """Build a chord line preserving positions."""
    if not show_chords:
        return ''
    chars: list[str] = []
    for idx, ch in enumerate(line.chords):
        while len(chars) < line.chord_positions[idx]:
            chars.append(' ')
        token = ch or ''
        chars.extend(list(token))
    return ''.join(chars)


def render_parsed_song(parsed: ParsedSong, show_chords: bool) -> str:
    """Render a parsed song into HTML with monospace alignment."""
    parts: list[str] = []
    for section in parsed.sections:
        parts.append('<section class="song-section">')
        parts.append(f'<h3 class="section-header">{escape(section.name)}</h3>')
        for line in section.lines:
            chord_line = build_chord_line(line, show_chords)
            lyric_line = escape(line.lyrics)
            if chord_line:
                parts.append('<pre class="chords">' + escape(chord_line) + '</pre>')
            parts.append('<pre class="lyrics">' + lyric_line + '</pre>')
        parts.append('</section>')
    return ''.join(parts)
