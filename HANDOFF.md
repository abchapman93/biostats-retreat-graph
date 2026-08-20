# Retreat EHR Knowledge-Graph — Handoff (2026-08-20)

**For:** Codex, continuing the scale round.
**Working dir:** `/Users/alecchapman/Code/Claude Setup/apps/retreat-ehr-graph/`
**Full plan/context:** `~/.claude/plans/dan-is-hosting-the-adaptive-cascade.md`
**Deadline:** biostatistics retreat is Friday; Dan is presenting the EHR-data topic.

---

## Current state

The **pilot (4 authors) is complete and verified** end-to-end: retrieve -> classify -> build ->
render all work, viewer is static/CDN-free/Pages-safe. The **scale round (9 authors) has not
started** — its briefs are staged. Your job: run the scale round through the same pipeline and
merge into the full 13-author graph.

| Piece | Status |
|---|---|
| Pilot authors resolved (4) | ✅ `authors.yaml` |
| Pilot retrieval (175 raw records) | ✅ `raw-candidates.jsonl` |
| Pilot classification (98 papers) | ✅ `papers.jsonl` |
| Builder + static viewer | ✅ `build_graph.py`, `index.html` (all DoD gates passed) |
| Real graph (112 nodes / 249 edges) | ✅ `graph-data.js` |
| Subtopic taxonomy | ✅ LOCKED (10 labels, below) |
| Scale round (9 authors) | ❌ not started — briefs staged |
| Retreat polish (legend relabel, EHR toggle) | ❌ optional, after scale |

---

## The pipeline (one round)

`disambiguation -> merge authors.yaml -> retrieval -> classification -> merge papers.jsonl -> rebuild graph -> verify`

## Locked taxonomy (10 subtopics — DO NOT drift; reuse labels exactly)

`clinical-application`, `causal-inference`, `survival-analysis`, `ehr-phenotyping`,
`missing-data`, `machine-learning-prediction`, `measurement-error`,
`treatment-effect-heterogeneity`, `sensitivity-analysis`, `bayesian-methods`.

---

## Immediate next steps (scale round — 9 authors, in order)

Remaining roster: **students** `christian-dalton`, `julia-bohman`, `yidan-zhang`, `yongjun-lee`,
`ravinder-singh`; **faculty** `xuan-wang`, `jincheng-shen`, `bernardo-modenesi`, `yue-zhang`.

### Step 1 — Disambiguation
Resolve each person's OpenAlex author id. Use `https://api.openalex.org/authors?search=<name>` +
web search; require **University of Utah** affiliation (ROR `03r0ha626`) AND biostat/epi/health
topic plausibility. **HIGH collision risk:** `ravinder-singh`, `yue-zhang`, `xuan-wang`,
`yidan-zhang`, `yongjun-lee` — do NOT accept a bare name match; mark `status: ambiguous` if unsure.
Students may have zero indexed papers -> `status: none` (fine). Write `authors-round2.yaml` (schema
matches `authors.yaml`). **A human (Alec) reviews the common names before merge — surface them.**

### Step 2 — Merge
Append the resolved round-2 authors into `authors.yaml`'s `authors:` list. **NEVER overwrite or
truncate the 4 pilot entries.**

### Step 3 — Retrieval (metadata + abstracts only)
For each resolved author, pull OpenAlex works since 2021:
`https://api.openalex.org/works?filter=author.id:<A...>,from_publication_date:2021-01-01&per-page=200&cursor=*&mailto=abchapman93@gmail.com`
Follow `meta.next_cursor` to exhaustion; reconstruct abstracts from `abstract_inverted_index`
(null -> empty, invent nothing); set a `likely_noise` bool on clearly-unrelated same-name records.
Append to `raw-candidates-round2.jsonl` (same record shape as `raw-candidates.jsonl`). No full text.

### Step 4 — Classification
**Follow `CLASSIFY-BRIEF-round2.md` exactly** — it pins the locked taxonomy, the EHR-relevance rule,
within-round + cross-round dedup, slug-collision avoidance, and the DoD. Output `papers-round2.jsonl`.
**Do NOT touch `papers.jsonl`.**

### Step 5 — Merge + rebuild + verify
Merge `papers-round2.jsonl` into `papers.jsonl`, unioning `roster_authors` on cross-round shared
papers (match by `openalex_id` then `doi`). Then rebuild and verify:
```bash
python3 build_graph.py --papers papers.jsonl
node -e 'global.window={};require("./graph-data.js");const g=window.GRAPH;const ids=new Set(g.nodes.map(n=>n.id));for(const e of g.edges){if(!ids.has(e.source)||!ids.has(e.target)){console.error("DANGLING",e);process.exit(1)}}console.log("nodes",g.nodes.length,"edges",g.edges.length,g.stats.by_type)'
```
Confirm: no dangling edges; `person` count == number of resolved authors (<= 13; some students may
be `none`); spot-check a few EHR + subtopic tags against abstracts.

---

## Key decisions (do not re-litigate)

- **Scope flexible:** every paper tagged for BOTH `ehr_relevant` and subtopic; the graph filters to
  EHR-only or shows all. EHR is a tag, not a gate — keep `ehr_relevant:false` papers.
- **Viewer reuses the wiki_viewer node types** (person=author, paper=paper, concept=subtopic) so no
  frontend schema edits are needed.
- **Retrieval = direct OpenAlex API**, not the `/lit-review` harness (harness needs an unbuilt
  Stage-1 run folder; not worth it for one-shot author pulls).
- **Classification for scale rounds = Codex** (Alec's call), against the LOCKED taxonomy.
- **Public build shows metadata only, never abstracts** (copyright). Abstracts stay local in
  `papers.jsonl` / raw files and are dropped from `graph-data.js` by the builder.
- Codex sandbox has no network; `vis-network.min.js` is already vendored locally.

## Gotchas

- **NEVER overwrite `authors.yaml` or `papers.jsonl`.** The pilot build once clobbered `authors.yaml`
  with a stub (recovered). Always write `*-round2` files and merge.
- `build_graph.py` uses a homegrown YAML reader (no PyYAML). `authors.yaml` uses folded (`>`)
  evidence blocks — parses fine; keep the formatting simple.
- **The two Xus are DIFFERENT people** (`yizhen-xu` = Biostatistics/Brown/JHU; `yizhe-crystal-xu` =
  Epidemiology/Utah/Stanford). Both OpenAlex records carry same-surname noise. Keep them separate;
  they must share 0 papers.
- `build_graph.py` fails nonzero on an unknown author slug in `papers.jsonl` — that's the join guard,
  not a bug.

## Optional / after scale

- Retreat polish (plan Step 2.4): relabel legend to Author/Publication/Subtopic; add an EHR-only
  toggle (filter papers on `ehr_relevant`, prune orphaned author/concept nodes).
- Spot-check the ~7 low-confidence pilot tags (empty-abstract / preprint-dup edge cases; see the
  classification notes).
- Publishing to GitHub Pages is a **separate explicit step** — Alec's call, not automatic.

## File map

| File | Role |
|---|---|
| `authors.yaml` | Roster + disambiguation (4 pilot authors; append round-2 here) |
| `authors-round2.yaml` | (to create) round-2 disambiguation output before merge |
| `raw-candidates.jsonl` | Pilot raw OpenAlex records (175) |
| `raw-candidates-round2.jsonl` | (to create) round-2 raw records |
| `papers.jsonl` | Master classified papers (98; merge round-2 in) |
| `papers-round2.jsonl` | (to create) round-2 classified output |
| `build_graph.py` | papers.jsonl + authors.yaml -> graph-data.js (validates slugs) |
| `graph-data.js` | `window.GRAPH` payload the viewer loads (rebuild after merge) |
| `index.html` | Static vis.js viewer (no CDN, no fetch; file:// + Pages safe) |
| `vis-network.min.js` | Vendored vis-network 9.1.9 (local, no CDN) |
| `sample-papers.jsonl` | Fixture for build_graph.py self-test |
| `BUILD-BRIEF.md` | The (completed) viewer/builder build brief |
| `CLASSIFY-BRIEF-round2.md` | The round-2 classification brief — follow for Step 4 |

## Repo state

The whole `apps/retreat-ehr-graph/` folder is **untracked / uncommitted** on `main`
(HEAD `8430f2b`). Not committed — Alec's call whether/when to commit.

## To preview the current pilot graph
```bash
cd apps/retreat-ehr-graph && python3 -m http.server 8793
# open http://127.0.0.1:8793/index.html
```
