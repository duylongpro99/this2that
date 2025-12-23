"""Doc-fetch orchestration for Context7 integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol, Sequence

_QUERY_ORDER = ("config_format", "instruction_precedence", "examples")

DEFAULT_QUERY_TEMPLATES: dict[str, str] = {
    "config_format": (
        "Find the official, up-to-date documentation for {agent_name} configuration files.\n"
        "Return the canonical filename(s), expected location(s), and required structure.\n"
        "Include any size limits, required headings, or reserved sections.\n"
        "Provide citations and the doc version or last-updated date when available."
    ),
    "instruction_precedence": (
        "Find the official documentation for {agent_name} instruction precedence.\n"
        "Describe how global, project, and nested config files are discovered and merged.\n"
        "Include the exact precedence order, override rules, and any special cases.\n"
        "Provide citations and the doc version or last-updated date when available."
    ),
    "examples": (
        "Find official example configurations for {agent_name}.\n"
        "Return a minimal example and a full example if available.\n"
        "Include headings, section ordering, and any recommended best practices.\n"
        "Provide citations and the doc version or last-updated date when available."
    ),
}


@dataclass(frozen=True)
class DocFetchRequest:
    agent_name: str
    agent_id: str
    config_scope: str | None = None


@dataclass(frozen=True)
class DocFetchQuery:
    topic: str
    query: str


@dataclass(frozen=True)
class DocSnippet:
    topic: str
    source: str
    content: str
    version: str | None = None


@dataclass(frozen=True)
class DocFetchPlan:
    mode: str
    queries: tuple[DocFetchQuery, ...]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class DocFetchResult:
    mode: str
    queries: tuple[DocFetchQuery, ...]
    snippets: tuple[DocSnippet, ...]


class DocFetcher(Protocol):
    def fetch(
        self, request: DocFetchRequest, queries: Sequence[DocFetchQuery]
    ) -> Sequence[DocSnippet]:
        """Fetch documentation snippets for the requested queries."""


def build_context7_queries(
    request: DocFetchRequest,
    templates: Mapping[str, str] | None = None,
) -> list[DocFetchQuery]:
    selected = templates or DEFAULT_QUERY_TEMPLATES
    format_data = {
        "agent_name": request.agent_name,
        "agent_id": request.agent_id,
        "config_scope": request.config_scope or "",
    }
    queries: list[DocFetchQuery] = []
    for topic in _QUERY_ORDER:
        template = selected.get(topic)
        if not template:
            continue
        query = template.format(**format_data)
        if request.config_scope and "{config_scope}" not in template:
            query = f"{query}\nFocus on {request.config_scope} scope when relevant."
        queries.append(DocFetchQuery(topic=topic, query=query))
    return queries


class DocFetchOrchestrator:
    def __init__(self, fetcher: DocFetcher | None = None, prefer_llm_direct: bool = True) -> None:
        self._fetcher = fetcher
        self._prefer_llm_direct = prefer_llm_direct

    def plan(
        self,
        request: DocFetchRequest,
        templates: Mapping[str, str] | None = None,
    ) -> DocFetchPlan:
        queries = tuple(build_context7_queries(request, templates))
        if self._prefer_llm_direct:
            return DocFetchPlan(mode="llm_direct", queries=queries)
        if self._fetcher is None:
            return DocFetchPlan(
                mode="llm_direct",
                queries=queries,
                warnings=("fallback_fetcher_unavailable",),
            )
        return DocFetchPlan(mode="fallback_fetcher", queries=queries)

    def fetch(
        self,
        request: DocFetchRequest,
        templates: Mapping[str, str] | None = None,
    ) -> DocFetchPlan | DocFetchResult:
        plan = self.plan(request, templates)
        if plan.mode != "fallback_fetcher":
            return plan
        if self._fetcher is None:
            return DocFetchPlan(
                mode="llm_direct",
                queries=plan.queries,
                warnings=("fallback_fetcher_unavailable",),
            )
        snippets = tuple(self._fetcher.fetch(request, plan.queries))
        return DocFetchResult(mode="fallback_fetcher", queries=plan.queries, snippets=snippets)
