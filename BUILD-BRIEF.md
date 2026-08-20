# Codex build brief — retreat EHR knowledge-graph viewer

You (Codex) are building the **static visualization** half of a retreat project. This is
the deterministic, local, no-network work. Retrieval and classification of real papers are
handled separately — do **not** do them. Build against the contract below and self-test with
a small fixture; real data lands later.

Working dir: `/Users/alecchapman/Code/Claude Setup`. All output goes in `apps/retreat-ehr-graph/`.

## Read first
- `~/.claude/plans/dan-is-hosting-the-adaptive-cascade.md` — the approved plan (context; you already reviewed it).
- `app/templates/wiki_viewer.html` — the viewer you will COPY and patch. Do not edit it in place.
- `tools/wiki_lib.py` — defines the `{nodes, edges, stats}` contract + type/color/shape maps you must match.
- `apps/retreat-ehr-graph/vis-network.min.js` — already vendored (v9.1.9). Use it locally.

## What to build

### 1. `apps/retreat-ehr-graph/build_graph.py`
Reads two inputs and writes `graph-data.js`. Pure stdlib (no pip installs). Deterministic
output ordering (sort nodes/edges by id) so diffs are stable.

**Inputs:**
- `authors.yaml` — registry. Each author: `slug` (canonical id), `name`, `aliases[]`,
  `role` (student|faculty), `orcid`, `openalex_author_id`, `faculty_page_url`, `works_count`,
  `status` (resolved|none|ambiguous). File has a top-level `lookback_start` too. **`authors.yaml`
  already exists with real disambiguated data — NEVER overwrite, truncate, or regenerate it.
  Treat it as read-only input.** If you need a fixture, write a SEPARATE `sample-authors.yaml`
  and point build_graph.py at it via `--authors`. YAML is simple enough to parse with a minimal
  hand-rolled reader if PyYAML isn't available — but check `python3 -c "import yaml"` first and prefer it.
- `papers.jsonl` — one JSON object per line: `slug, title, year, venue, doi, pmid,
  openalex_id, roster_authors[] (author SLUGS), abstract, ehr_relevant (bool),
  ehr_role (uses-ehr|addresses-ehr-problem|na), subtopics[] (list of subtopic labels),
  confidence`. **`roster_authors` holds author slugs that MUST exist in authors.yaml — validate
  and fail loudly (nonzero exit, clear message) on an unknown slug.** Do NOT put `abstract`
  into the output (copyright — public site shows metadata only).

**Output `graph-data.js`** — a single assignment `window.GRAPH = { ... };` with this exact shape
(this is the shape the reused renderer requires — match it precisely):

```js
window.GRAPH = {
  nodes: [
    { id: "person:alec-chapman", type: "person", slug: "alec-chapman",
      label: "Alec Chapman", tier: null, exists: true, path: null,
      summary: "Student",                       // role for people; short label for others
      metadata: { inbound: 3 } },               // inbound = incoming edge count (concept sizing)
    { id: "paper:chapman-2024-foo", type: "paper", slug: "chapman-2024-foo",
      label: "Chapman 2024", tier: null, exists: true, path: null,
      summary: "Short title...",
      metadata: { inbound: 0, title: "...", venue: "...", year: 2024,
                  doi: "10.xxxx/yyy", ehr_relevant: true, ehr_role: "uses-ehr",
                  subtopics: ["causal-inference"] } },
    { id: "concept:missing-data", type: "concept", slug: "missing-data",
      label: "Missing data", tier: null, exists: true, path: null,
      summary: "Subtopic", metadata: { inbound: 5 } }
  ],
  edges: [
    { source: "person:alec-chapman", target: "paper:chapman-2024-foo", section: "author" },
    { source: "paper:chapman-2024-foo", target: "concept:causal-inference", section: "subtopic" }
  ],
  stats: { total_nodes: 3, total_edges: 2, wanted: 0,
           by_type: { person: 1, paper: 1, concept: 1 } }
};
```

**Node construction rules:**
- author -> `type: "person"`, id `person:<author-slug>`, `summary` = role.
- paper -> `type: "paper"`, id `paper:<paper-slug>`, `label` = "`<FirstAuthorLastname> <year>`"
  (derive lastname from the paper slug or first roster author's name), `metadata` carries
  title/venue/year/doi/ehr_relevant/ehr_role/subtopics.
- subtopic -> `type: "concept"`, id `concept:<subtopic-slug>` (kebab-case the label),
  `label` = the human label. One concept node per distinct subtopic across all papers.
- Each paper appears **once** even if multiple roster authors co-wrote it (dedupe by paper slug);
  emit one author->paper edge per roster author (this creates the shared cross-links).
- Compute `metadata.inbound` = number of edges pointing at each node.
- `tier: null`, `exists: true`, `path: null` for all nodes.

### 2. `apps/retreat-ehr-graph/index.html`
Copy `app/templates/wiki_viewer.html`, then strip ALL server coupling. There are **three**
`fetch()` calls (confirmed) — handle each:
- `fetch("api/graph")` -> use the embedded `window.GRAPH` (add `<script src="graph-data.js"></script>`
  before the app script). Remove the fetch.
- `fetch("api/page/<type>/<slug>")` (the click-to-preview detail panel) -> **rewrite to a
  metadata-only renderer** that reads the clicked node's `metadata`/`summary` from `window.GRAPH`.
  For a paper: show title, venue, year, and a DOI link (`https://doi.org/<doi>`), EHR role, subtopics.
  For a person/concept: show label + inbound/degree counts. No markdown, no server call.
- `POST api/shutdown` (the "Done"/close control) -> make it a local no-op (or remove the control).

Then remove BOTH external CDN scripts and rely only on the local vendored file:
- Replace the unpkg `vis-network` `<script src>` with `<script src="vis-network.min.js"></script>`.
- **Remove the `marked` (jsDelivr) script and all markdown rendering** — the metadata-only panel
  needs no markdown. Delete the `marked(...)` calls.

Result: `index.html` loads with **zero external hosts**, works opened via `file://` (double-click)
AND served over HTTP under a subpath (GitHub Pages). Preserve the existing vis.js graph rendering,
force layout, type filters, search, and legend — only the data source and detail panel change.

## Out of scope (do NOT do)
- No retrieval, no OpenAlex/PubMed calls, no classification, no writing real `papers.jsonl`.
- No Flask, no server code, no `git push`, no GitHub Pages enablement.
- Do not edit `app/templates/wiki_viewer.html` or `tools/wiki_lib.py` — copy/read only.
- The EHR-only toggle and legend relabel are OPTIONAL polish — implement only if the core builds
  cleanly and time allows; if you do, follow the toggle spec in the plan (filter on paper
  `ehr_relevant`, prune orphaned author/concept nodes).

## Definition of done (bash-checkable — run these and report output)
1. Create a fixture to self-test (since real data isn't ready):
   `apps/retreat-ehr-graph/sample-papers.jsonl` with ~4 papers referencing real pilot author
   slugs (`alec-chapman`, `daniel-scharfstein`, `yizhen-xu`, `yizhe-crystal-xu`), including at
   least one co-authored paper (two roster authors) and a mix of `ehr_relevant` true/false.
2. `cd "/Users/alecchapman/Code/Claude Setup/apps/retreat-ehr-graph" && python3 build_graph.py --papers sample-papers.jsonl`
   exits 0 and writes `graph-data.js`.
3. `node -e "global.window={}; require('./apps/retreat-ehr-graph/graph-data.js'); const g=window.GRAPH;
   if(!g.nodes.length||!g.edges.length) process.exit(1);
   const ids=new Set(g.nodes.map(n=>n.id));
   for(const e of g.edges){ if(!ids.has(e.source)||!ids.has(e.target)){console.error('dangling edge',e);process.exit(1);} }
   console.log('nodes',g.nodes.length,'edges',g.edges.length,'stats',JSON.stringify(g.stats));"`
   passes (no dangling edges; co-authored paper is a single node with 2 author edges).
4. Feed build_graph.py a papers.jsonl line whose `roster_authors` contains an unknown slug ->
   it exits nonzero with a clear error (prove the validation).
5. `grep -c "unpkg\|jsdelivr\|cdnjs\|https://" apps/retreat-ehr-graph/index.html` -> **0**
   (no external hosts remain; DOI links built in JS at click time are fine, but no `<script src>`
   or `<link href>` to a remote host).
6. `grep -c "fetch(" apps/retreat-ehr-graph/index.html` -> **0** (all three fetches gone).
7. Serve-and-load smoke: `cd apps/retreat-ehr-graph && (python3 -m http.server 8791 &) ` then
   `curl -sf http://127.0.0.1:8791/index.html >/dev/null && curl -sf http://127.0.0.1:8791/graph-data.js >/dev/null`
   both succeed; kill the server. (Confirms relative paths resolve under an HTTP subpath.)

## Model/effort
Standard multi-file build with a clear spec -> medium effort, default model. No override needed.

## Handback
End with a HANDBACK block: which DoD checks passed (paste command output for 2-7), files created,
anything you couldn't verify, and any contract ambiguity you had to resolve. Do not claim done
without the DoD output.
