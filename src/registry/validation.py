"""Registry validation helpers."""

from __future__ import annotations

import re

from .models import AgentRegistry, default_registry


class UnknownAgentError(ValueError):
    """Raised when an agent cannot be resolved in the registry."""


_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")


def normalize_agent_name(name: str) -> str:
    return _NORMALIZE_RE.sub("", name.strip().lower())


def resolve_agent_id(name: str, registry: AgentRegistry | None = None) -> str:
    registry = registry or default_registry()
    normalized = normalize_agent_name(name)
    if not normalized:
        raise UnknownAgentError("agent name is required")
    for agent in registry.agents:
        if normalize_agent_name(agent.agent_id) == normalized:
            return agent.agent_id
        for alias in agent.aliases:
            if normalize_agent_name(alias) == normalized:
                return agent.agent_id
    supported = ", ".join(sorted(agent.agent_id for agent in registry.agents))
    raise UnknownAgentError(f"unknown agent '{name}'; supported agents: {supported}")
