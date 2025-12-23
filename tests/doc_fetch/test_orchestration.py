from __future__ import annotations

from src import doc_fetch


def test_build_context7_queries_includes_scope_hint() -> None:
    request = doc_fetch.DocFetchRequest(
        agent_name="Claude",
        agent_id="claude",
        config_scope="project",
    )

    queries = doc_fetch.build_context7_queries(request)

    assert [query.topic for query in queries] == [
        "config_format",
        "instruction_precedence",
        "examples",
    ]
    assert "Claude" in queries[0].query
    assert "Focus on project scope" in queries[0].query


def test_orchestrator_prefers_llm_direct() -> None:
    request = doc_fetch.DocFetchRequest(agent_name="Codex", agent_id="codex")
    orchestrator = doc_fetch.DocFetchOrchestrator(fetcher=_DummyFetcher(), prefer_llm_direct=True)

    plan = orchestrator.plan(request)

    assert plan.mode == "llm_direct"


def test_orchestrator_falls_back_to_fetcher() -> None:
    request = doc_fetch.DocFetchRequest(agent_name="Gemini", agent_id="gemini")
    fetcher = _DummyFetcher()
    orchestrator = doc_fetch.DocFetchOrchestrator(fetcher=fetcher, prefer_llm_direct=False)

    result = orchestrator.fetch(request)

    assert isinstance(result, doc_fetch.DocFetchResult)
    assert result.mode == "fallback_fetcher"
    assert result.snippets[0].content == "doc snippet"
    assert fetcher.called


def test_orchestrator_warns_when_fallback_missing() -> None:
    request = doc_fetch.DocFetchRequest(agent_name="Kiro", agent_id="kiro")
    orchestrator = doc_fetch.DocFetchOrchestrator(fetcher=None, prefer_llm_direct=False)

    plan = orchestrator.plan(request)

    assert plan.mode == "llm_direct"
    assert "fallback_fetcher_unavailable" in plan.warnings


def test_orchestrator_caches_fallback_fetcher() -> None:
    request = doc_fetch.DocFetchRequest(agent_name="Claude", agent_id="claude")
    fetcher = _CountingFetcher()
    cache = doc_fetch.DocFetchCache(ttl_seconds=60.0)
    orchestrator = doc_fetch.DocFetchOrchestrator(
        fetcher=fetcher,
        prefer_llm_direct=False,
        cache=cache,
    )

    first = orchestrator.fetch(request)
    second = orchestrator.fetch(request)

    assert fetcher.calls == 1
    assert isinstance(first, doc_fetch.DocFetchResult)
    assert isinstance(second, doc_fetch.DocFetchResult)
    assert first.snippets == second.snippets


def test_orchestrator_cache_expires() -> None:
    request = doc_fetch.DocFetchRequest(agent_name="Gemini", agent_id="gemini")
    fetcher = _CountingFetcher()
    now = [0.0]

    def _now() -> float:
        return now[0]

    cache = doc_fetch.DocFetchCache(ttl_seconds=5.0, now_fn=_now)
    orchestrator = doc_fetch.DocFetchOrchestrator(
        fetcher=fetcher,
        prefer_llm_direct=False,
        cache=cache,
    )

    orchestrator.fetch(request)
    now[0] = 10.0
    orchestrator.fetch(request)

    assert fetcher.calls == 2


class _DummyFetcher:
    def __init__(self) -> None:
        self.called = False

    def fetch(self, request, queries):
        self.called = True
        return [
            doc_fetch.DocSnippet(
                topic=queries[0].topic,
                source="https://example.com",
                content="doc snippet",
                version="v1",
            )
        ]


class _CountingFetcher:
    def __init__(self) -> None:
        self.calls = 0

    def fetch(self, request, queries):
        self.calls += 1
        return [
            doc_fetch.DocSnippet(
                topic=queries[0].topic,
                source="https://example.com",
                content="doc snippet",
                version="v1",
            )
        ]
