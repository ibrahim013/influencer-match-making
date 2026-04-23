from __future__ import annotations

# Approximate list prices per 1M tokens (USD), for log-scale cost hints only.
# Source: public OpenAI pricing snapshots — refresh periodically.
_PER_MILLION: dict[str, dict[str, float]] = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-4": {"input": 30.00, "output": 60.00},
}


def estimate_llm_cost_usd(
    *,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
) -> float | None:
    """Rough USD estimate from token counts; not billing-grade."""
    rates = _PER_MILLION.get(model.strip())
    if not rates:
        for key, val in _PER_MILLION.items():
            if key in model:
                rates = val
                break
    if not rates:
        return None
    inp = rates["input"] * prompt_tokens / 1_000_000
    out = rates["output"] * completion_tokens / 1_000_000
    return round(inp + out, 6)


def extract_token_usage(response: object) -> dict[str, int | None]:
    """Normalize token counts from LangChain LLMResult."""
    from langchain_core.outputs import LLMResult

    if not isinstance(response, LLMResult):
        return {
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
        }

    usage: dict[str, int] = {}
    lo = response.llm_output or {}
    raw = lo.get("token_usage")
    if isinstance(raw, dict):
        usage = {k: int(v) for k, v in raw.items() if isinstance(v, (int, float))}

    if not usage and response.generations:
        try:
            gen0 = response.generations[0][0]
            msg = getattr(gen0, "message", None)
            um = getattr(msg, "usage_metadata", None) if msg is not None else None
            if isinstance(um, dict):
                pt = um.get("input_tokens") or um.get("prompt_tokens")
                ct = um.get("output_tokens") or um.get("completion_tokens")
                tt = um.get("total_tokens")
                if pt is not None:
                    usage["prompt_tokens"] = int(pt)
                if ct is not None:
                    usage["completion_tokens"] = int(ct)
                if tt is not None:
                    usage["total_tokens"] = int(tt)
        except (IndexError, TypeError, ValueError):
            pass

    pt = usage.get("prompt_tokens")
    ct = usage.get("completion_tokens")
    tt = usage.get("total_tokens")
    if tt is None and pt is not None and ct is not None:
        tt = pt + ct
    return {
        "prompt_tokens": pt,
        "completion_tokens": ct,
        "total_tokens": tt,
    }


def model_name_from_serialized(serialized: dict[str, object] | None) -> str | None:
    if not isinstance(serialized, dict):
        return None
    kwargs = serialized.get("kwargs")
    if isinstance(kwargs, dict):
        m = kwargs.get("model_name") or kwargs.get("model")
        if isinstance(m, str):
            return m
    return None
