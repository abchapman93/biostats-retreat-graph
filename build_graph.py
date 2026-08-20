#!/usr/bin/env python3
"""Build deterministic static graph data for the retreat EHR viewer."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.lower() in {"null", "~"}:
        return None
    if value.startswith("[") and value.endswith("]"):
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            parsed = [item.strip().strip("'\\\"") for item in value[1:-1].split(",")]
        return list(parsed)
    return value.strip("'\\\"")


def load_authors(path: Path) -> dict[str, dict[str, Any]]:
    """Load the simple author registry without requiring PyYAML."""
    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None

    if yaml is not None:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        records = data.get("authors", [])
    else:
        records: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.split("#", 1)[0].rstrip()
            if not line.strip() or line.lstrip() == "authors:":
                continue
            match = re.match(r"^\s{2}-\s+([A-Za-z_][\w-]*):\s*(.*)$", line)
            if match:
                current = {match.group(1): parse_scalar(match.group(2))}
                records.append(current)
                continue
            match = re.match(r"^\s{4}([A-Za-z_][\w-]*):\s*(.*)$", line)
            if match and current is not None:
                current[match.group(1)] = parse_scalar(match.group(2))

    authors: dict[str, dict[str, Any]] = {}
    for record in records:
        slug = record.get("slug")
        if not isinstance(slug, str) or not slug:
            raise ValueError(f"author registry entry is missing a slug in {path}")
        if slug in authors:
            raise ValueError(f"author registry contains duplicate slug: {slug}")
        authors[slug] = record
    if not authors:
        raise ValueError(f"author registry has no authors: {path}")
    return authors


def kebab_case(label: str) -> str:
    normalized = unicodedata.normalize("NFKD", label).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-")
    if not slug:
        raise ValueError(f"subtopic cannot become a slug: {label!r}")
    return slug


def paper_label(paper: dict[str, Any], authors: dict[str, dict[str, Any]]) -> str:
    roster = paper.get("roster_authors") or []
    if roster:
        name = str(authors[roster[0]].get("name") or roster[0])
        lastname = name.split()[-1]
    else:
        lastname = str(paper["slug"]).split("-")[0].title()
    return f"{lastname} {paper.get('year', '')}".strip()


def read_papers(path: Path, authors: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    papers: dict[str, dict[str, Any]] = {}
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            paper = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{number}: invalid JSON: {exc.msg}") from exc
        slug = paper.get("slug")
        if not isinstance(slug, str) or not slug:
            raise ValueError(f"{path}:{number}: paper is missing slug")
        roster = paper.get("roster_authors")
        if not isinstance(roster, list):
            raise ValueError(f"{path}:{number}: paper {slug!r} has no roster_authors list")
        for author_slug in roster:
            if author_slug not in authors:
                raise ValueError(
                    f"{path}:{number}: paper {slug!r} references unknown author slug {author_slug!r}"
                )
        papers.setdefault(slug, paper)
    return papers


def build_graph(authors: dict[str, dict[str, Any]], papers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: set[tuple[str, str, str]] = set()

    for slug, author in authors.items():
        if author.get("status") != "resolved":
            continue
        nodes[f"person:{slug}"] = {
            "id": f"person:{slug}", "type": "person", "slug": slug,
            "label": author.get("name") or slug, "tier": None, "exists": True,
            "path": None, "summary": author.get("role") or "", "metadata": {"inbound": 0},
        }

    for slug, paper in papers.items():
        paper_id = f"paper:{slug}"
        subtopics = paper.get("subtopics") or []
        if not isinstance(subtopics, list):
            raise ValueError(f"paper {slug!r} has non-list subtopics")
        nodes[paper_id] = {
            "id": paper_id, "type": "paper", "slug": slug,
            "label": paper_label(paper, authors), "tier": None, "exists": True,
            "path": None, "summary": str(paper.get("title") or "")[:160],
            "metadata": {
                "inbound": 0, "title": paper.get("title") or "",
                "venue": paper.get("venue") or "", "year": paper.get("year"),
                "doi": paper.get("doi") or "", "ehr_relevant": bool(paper.get("ehr_relevant")),
                "ehr_role": paper.get("ehr_role") or "na", "subtopics": subtopics,
                # The collection currently retains only the ordered subset of
                # division coauthors.  That order is the deterministic fallback
                # for the display anchor when first/senior authorship metadata is
                # unavailable.
                "primary_author": paper["roster_authors"][0] if paper["roster_authors"] else None,
            },
        }
        for author_slug in paper["roster_authors"]:
            edges.add((f"person:{author_slug}", paper_id, "author"))
        for subtopic in subtopics:
            if not isinstance(subtopic, str) or not subtopic.strip():
                raise ValueError(f"paper {slug!r} has invalid subtopic {subtopic!r}")
            concept_slug = kebab_case(subtopic)
            concept_id = f"concept:{concept_slug}"
            nodes.setdefault(concept_id, {
                "id": concept_id, "type": "concept", "slug": concept_slug,
                "label": subtopic, "tier": None, "exists": True, "path": None,
                "summary": "Subtopic", "metadata": {"inbound": 0},
            })
            edges.add((paper_id, concept_id, "subtopic"))

    sorted_edges = [
        {"source": source, "target": target, "section": section}
        for source, target, section in sorted(edges)
    ]
    inbound = Counter(edge["target"] for edge in sorted_edges)
    sorted_nodes = [nodes[node_id] for node_id in sorted(nodes)]
    for node in sorted_nodes:
        node["metadata"]["inbound"] = inbound[node["id"]]

    by_type = Counter(node["type"] for node in sorted_nodes)
    return {
        "nodes": sorted_nodes,
        "edges": sorted_edges,
        "stats": {
            "total_nodes": len(sorted_nodes), "total_edges": len(sorted_edges), "wanted": 0,
            "by_type": {node_type: by_type[node_type] for node_type in sorted(by_type)},
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    parser.add_argument("--authors", type=Path, default=here / "authors.yaml")
    parser.add_argument("--papers", type=Path, default=here / "papers.jsonl")
    parser.add_argument("--output", type=Path, default=here / "graph-data.js")
    args = parser.parse_args()

    try:
        authors = load_authors(args.authors)
        papers = read_papers(args.papers, authors)
        graph = build_graph(authors, papers)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    args.output.write_text(
        "window.GRAPH = " + json.dumps(graph, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
