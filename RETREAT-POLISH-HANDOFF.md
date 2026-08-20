# Retreat EHR Knowledge Graph — Retreat Polish Handoff (2026-08-20)

**For:** a fresh implementation session

**Working directory:** `/Users/alecchapman/Code/Claude Setup/apps/retreat-ehr-graph/`

**Scope:** make the static graph easier to present at the biostatistics retreat. This is viewer-only polish; the scale retrieval/classification round is complete.

## Current verified state

- `authors.yaml`: 13 roster entries; 12 `status: resolved` authors render as graph persons. Yongjun Lee is `status: none` and intentionally is not rendered.
- `papers.jsonl`: 393 classified papers.
- `graph-data.js`: 415 nodes (12 people, 393 papers, 10 subtopics) and 1,131 edges; 138 paper nodes have `metadata.ehr_relevant === true`.
- The graph is static and self-contained: `index.html` loads `graph-data.js` and the vendored `vis-network.min.js`; it must keep working both from `file://` and GitHub Pages.
- The app folder is untracked/uncommitted on `main` (HEAD `8430f2b`). Do not switch branches or publish/deploy.

## Goal

Make two surgical updates to `index.html`:

1. Relabel the legend for the three graph types that actually appear:
   - `person` → **Author**
   - `paper` → **Publication**
   - `concept` → **Subtopic**

   Remove the unused generic legend entries (`project`, `method`, `synthesis`) and the irrelevant “wanted page” note. Do not change node colors or shapes.

2. Add an **EHR-only** checkbox, defaulting to off. When enabled, show only:
   - paper nodes whose `metadata.ehr_relevant === true`; and
   - author/subtopic nodes adjacent to at least one such visible paper.

   Hide non-EHR papers and author/subtopic nodes left without a visible paper connection. The toggle must work with the existing type filters, search directory, neighborhood control, reset, and node click behavior.

## Implementation notes

- The topbar controls are near `index.html` lines 493–514. Add the checkbox there (or in a comparably compact sidebar location) with a clear label such as `EHR only`.
- Viewer state begins near line 606. The existing filter/render flow is in `nodePassesFilters()`, `buildEntityDirectory()`, and `render()` (roughly lines 794–1,000).
- `ehr_relevant` is available only on **paper** nodes as `node.metadata.ehr_relevant`. Derive the visible adjacent author/concept set from the existing `graphData.edges`; do not add fields to `graph-data.js` or modify `build_graph.py`.
- Apply the EHR selection before rendering both nodes and edges. The entity directory must use the same selection so it does not list hidden orphan authors/subtopics.
- Preserve the viewer’s static behavior: no `fetch()`, no external CDN/resource, no backend/API calls, no new dependencies.
- Preserve all data files (`authors*.yaml`, `raw-candidates*.jsonl`, `papers*.jsonl`, `graph-data.js`) unless rebuilding `graph-data.js` becomes necessary to verify an unrelated existing change. This task should not require a rebuild.

## Acceptance criteria

1. The legend visibly says **Author**, **Publication**, and **Subtopic**, with no generic unused-type labels or “wanted page” explanation.
2. The unchecked graph shows the full existing graph (415 nodes / 1,131 edges).
3. Turning on **EHR only** renders exactly the EHR-relevant papers plus their adjacent author/subtopic nodes; it renders no `ehr_relevant:false` paper and no orphan author/subtopic.
4. Turning it off restores the full graph. Existing type filters, search/directory, neighborhood focus, reset, and preview continue to function.
5. The page remains self-contained and usable via both `file://` and HTTP. Do not publish it.

## Required verification

Run these after the edit and report real output:

```bash
cd apps/retreat-ehr-graph
node -e 'global.window={};require("./graph-data.js");const g=window.GRAPH;const ids=new Set(g.nodes.map(n=>n.id));for(const e of g.edges){if(!ids.has(e.source)||!ids.has(e.target)){console.error("DANGLING",e);process.exit(1)}}console.log("nodes",g.nodes.length,"edges",g.edges.length,g.stats.by_type)'
rg -n "EHR only|Author|Publication|Subtopic" index.html
! rg -n "fetch\\(|https?://" index.html
```

Then preview locally:

```bash
cd apps/retreat-ehr-graph
python3 -m http.server 8793
```

Manually verify the toggle in the browser. In particular, with the toggle enabled, inspect a visible paper and confirm its EHR role appears in the preview; then toggle it off and confirm a known non-EHR paper returns.

## Out of scope

- Reclassification, author disambiguation, retrieval, or any edits to the graph data.
- Changing node colors/shapes, reworking the overall layout, or making the generic wiki-viewer architecture more abstract.
- Git commits, branch changes, deployment, GitHub Pages enablement, or any public upload.

## HANDBACK format

End with:

```text
HANDBACK
- DoD: <each acceptance criterion> → MET/SLIPPED (+ command output)
- Files touched: <list>
- Commit: <SHA or "not committed">
- Flags / deviations: <...>
- Open questions: <...>
```

Include the manual toggle check in the DoD evidence. Codex’s handback is not acceptance; Alec/Claude will review the diff and rerun the gates.
