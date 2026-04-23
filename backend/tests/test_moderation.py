from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.agent.tools.moderation import validate_input


@pytest.mark.asyncio
async def test_validate_input_passes() -> None:
    result = MagicMock()
    result.flagged = False
    result.categories.model_dump = MagicMock(return_value={})
    client = MagicMock()
    client.moderations.create = AsyncMock(return_value=MagicMock(results=[result]))
    await validate_input("We are a sustainable beverage brand for families.", client)


@pytest.mark.asyncio
async def test_validate_input_blocks() -> None:
    result = MagicMock()
    result.flagged = True
    result.categories.model_dump = MagicMock(return_value={"harassment": True})
    client = MagicMock()
    client.moderations.create = AsyncMock(return_value=MagicMock(results=[result]))
    with pytest.raises(ValueError):
        await validate_input("bad content", client)
