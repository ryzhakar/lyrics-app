from __future__ import annotations

import re
from dataclasses import dataclass

CHORD_PATTERN = re.compile(r'\[([^\]]+)\]')
SECTION_START_PATTERN = re.compile(r'\{start_of_section:\s*([^}]+)\}', re.IGNORECASE)
SECTION_END_PATTERN = re.compile(r'\{end_of_section\}', re.IGNORECASE)


@dataclass(slots=True)
class LineBlock:
    """Represent a chord-lyrics aligned line."""

    chords: list[str | None]
    chord_positions: list[int]
    lyrics: str


@dataclass(slots=True)
class Section:
    """Represent a logical song section."""

    name: str
    lines: list[LineBlock]


@dataclass(slots=True)
class ParsedSong:
    """Represent a parsed song structure."""

    sections: list[Section]
    warnings: list[str]


class ParseError(Exception):
    """Represent an unrecoverable parse error."""


def tokenize_line(line: str) -> tuple[list[str | None], list[int], str]:
    """Tokenize a single line into chords, positions, lyrics."""
    chords: list[str | None] = []
    positions: list[int] = []
    lyrics_parts: list[str] = []
    last_index = 0
    removed_total = 0
    for m in CHORD_PATTERN.finditer(line):
        start, end = m.span()
        lyrics_parts.append(line[last_index:start])
        chord_text = m.group(1).strip()
        chords.append(chord_text)
        positions.append(start - removed_total)
        removed_total += end - start
        last_index = end
    lyrics_parts.append(line[last_index:])
    lyrics = ''.join(lyrics_parts)
    if not chords and not lyrics:
        return [], [], ''
    if not chords:
        return [], [], lyrics
    return chords, positions, lyrics


def parse_chordpro(content: str) -> ParsedSong:
    """Parse ChordPro content into a structured song."""
    sections: list[Section] = []
    current_section: Section | None = None
    warnings: list[str] = []
    for raw_line in content.splitlines():
        line = raw_line.rstrip('\n')
        if not line.strip():
            if current_section is not None:
                current_section.lines.append(LineBlock([], [], ''))
            continue
        start_match = SECTION_START_PATTERN.fullmatch(line.strip())
        end_match = SECTION_END_PATTERN.fullmatch(line.strip())
        if start_match:
            if current_section is not None:
                raise ParseError('Nested sections are not supported')
            section_name = start_match.group(1).strip()
            current_section = Section(section_name, [])
            continue
        if end_match:
            if current_section is None:
                raise ParseError('Unmatched section end')
            sections.append(current_section)
            current_section = None
            continue
        chords, positions, lyrics = tokenize_line(line)
        line_block = LineBlock(chords, positions, lyrics)
        if current_section is None:
            current_section = Section('section', [])
        current_section.lines.append(line_block)
    if current_section is not None:
        raise ParseError('Unclosed section detected')
    return ParsedSong(sections, warnings)


def strip_chordpro_to_lyrics(content: str) -> str:
    """Strip ChordPro markup to plain lyrics text."""
    text = CHORD_PATTERN.sub('', content)
    text = SECTION_START_PATTERN.sub('', text)
    text = SECTION_END_PATTERN.sub('', text)
    return text
