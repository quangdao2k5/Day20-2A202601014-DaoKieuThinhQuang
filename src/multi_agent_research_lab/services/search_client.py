"""Search client abstraction for ResearcherAgent."""

import json
import re
from pathlib import Path

from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client backed by the bundled offline corpus."""

    def __init__(self, corpus_dir: Path | None = None) -> None:
        self.corpus_dir = corpus_dir or Path("ai_agent_offline_research_corpus_v2/topics")

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search local JSON knowledge cards and source documents."""

        query_terms = _tokenize(query)
        scored: list[tuple[int, SourceDocument]] = []
        for path in sorted(self.corpus_dir.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue

            topic = payload.get("topic", {})
            topic_name = str(topic.get("name", path.stem))
            knowledge_base = payload.get("knowledge_base", {})

            for article in knowledge_base.get("knowledge_articles", []):
                title = str(article.get("title", "Untitled knowledge article"))
                content = str(article.get("content", ""))
                label = str(article.get("article_id", title))
                source = SourceDocument(
                    title=f"{topic_name}: {title}",
                    url=f"offline://{path.stem}#{label}",
                    snippet=_snippet(content),
                    metadata={
                        "source_id": label,
                        "topic": topic_name,
                        "kind": "knowledge_article",
                    },
                )
                scored.append((_score(query_terms, title, content, topic_name), source))

            for document in knowledge_base.get("source_documents", []):
                title = str(document.get("title", "Untitled source document"))
                content = str(document.get("full_text", ""))
                label = str(document.get("citation_label") or document.get("document_id") or title)
                source = SourceDocument(
                    title=title,
                    url=str(document.get("provenance_url") or f"offline://{path.stem}#{label}"),
                    snippet=_snippet(content),
                    metadata={
                        "source_id": label,
                        "topic": topic_name,
                        "kind": str(document.get("document_class", "source_document")),
                        "is_synthetic": bool(document.get("is_synthetic", False)),
                    },
                )
                scored.append((_score(query_terms, title, content, topic_name), source))

        scored.sort(key=lambda item: item[0], reverse=True)
        results = [source for score, source in scored if score > 0][:max_results]
        return results or [source for _, source in scored[:max_results]]


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", text.lower()) if len(token) > 2}


def _score(query_terms: set[str], *fields: str) -> int:
    combined = " ".join(fields).lower()
    haystack = _tokenize(combined)
    overlap = len(query_terms & haystack)
    return overlap * 10 + sum(1 for term in query_terms if term in combined)


def _snippet(text: str, limit: int = 520) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rsplit(" ", 1)[0] + "..."
