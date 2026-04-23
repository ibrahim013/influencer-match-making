from __future__ import annotations

import asyncio
import logging

from openai import AsyncOpenAI

from app.core.errors import ToolError

logger = logging.getLogger(__name__)


async def validate_input(brand_context: str, client: AsyncOpenAI) -> None:
    """
    Inbound moderation using the OpenAI Moderation API.
    Raises ValueError if content is flagged (mapped to HTTP 422 at the API layer).
    Retries transient transport failures up to 3 times.
    """
    last_err: Exception | None = None
    for attempt in range(3):
        try:
            resp = await client.moderations.create(input=brand_context)
            result = resp.results[0]
            if result.flagged:
                categories = [
                    k for k, v in result.categories.model_dump().items() if v
                ]
                logger.warning("Moderation flagged input categories=%s", categories)
                raise ValueError(
                    f"Brand context failed moderation review: categories={categories}"
                )
            return
        except ValueError:
            raise
        except Exception as e:
            last_err = e
            logger.warning("Moderation attempt %s failed: %s", attempt + 1, e)
            if attempt == 2:
                raise ToolError(f"Moderation API error: {e}") from e
            await asyncio.sleep(0.35 * (attempt + 1))

    raise ToolError(f"Moderation API error: {last_err}")
