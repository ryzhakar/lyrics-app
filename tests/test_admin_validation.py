from __future__ import annotations

import pytest

from app.admin import SongAdmin


@pytest.mark.asyncio
async def test_song_admin_on_model_change_accepts_valid_content() -> None:
    model = type('M', (), {'chordpro_content': '[C]Line'})()
    await SongAdmin.__dict__['on_model_change'](None, {}, model, True, object())


@pytest.mark.asyncio
async def test_song_admin_on_model_change_rejects_invalid_content() -> None:
    model = type('M', (), {'chordpro_content': ''})()
    with pytest.raises(Exception):
        await SongAdmin.__dict__['on_model_change'](
            None,
            {'chordpro_content': '{start_of_section: A}'},
            model,
            True,
            object(),
        )
