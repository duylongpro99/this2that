"""Registry data model and defaults."""

from .detection import AgentDetection, AgentDetectionMatch, detect_agent_configs
from .models import ArtifactKind, AgentArtifact, AgentDefinition, AgentRegistry, default_registry
from .validation import UnknownAgentError, normalize_agent_name, resolve_agent_id

__all__ = [
    "ArtifactKind",
    "AgentArtifact",
    "AgentDetection",
    "AgentDetectionMatch",
    "AgentDefinition",
    "AgentRegistry",
    "detect_agent_configs",
    "default_registry",
    "UnknownAgentError",
    "normalize_agent_name",
    "resolve_agent_id",
]
