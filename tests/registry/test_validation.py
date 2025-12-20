from __future__ import annotations

import pytest

from src.registry import UnknownAgentError, resolve_agent_id


def test_resolve_agent_id_accepts_alias_with_punctuation() -> None:
    assert resolve_agent_id("Claude.md") == "claude"


def test_resolve_agent_id_rejects_unknown_agent() -> None:
    with pytest.raises(UnknownAgentError, match="unknown agent"):
        resolve_agent_id("unknown-agent")
