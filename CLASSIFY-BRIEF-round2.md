# Codex classification brief — round 2 (scale roster)

Classify and deduplicate the round-2 retrieved records into `papers-round2.jsonl`, using a
FIXED taxonomy locked from the pilot. This is a judgment pass over abstracts, but the label
set is fixed — do not invent the taxonomy, apply it. Claude merges your output into the
master `papers.jsonl` afterward and verifies a sample.

Working dir: `/Users/alecchapman/Code/Claude Setup/apps/retreat-ehr-graph`.

## Input
- `raw-candidates-round2.jsonl` — one JSON object per (author, paper):
  `{author_slug, openalex_id, doi, pmid, title, venue, year, authors_list, abstract, work_type, likely_noise, source}`.
- `authors.yaml` — the full roster (read-only; contains all resolved author slugs). Use it only
  to know valid slugs. **NEVER modify authors.yaml.**
- `papers.jsonl` — the EXISTING pilot papers (read-only here). Use it for two things: (a) avoid
  slug collisions, (b) detect cross-round shared papers (see dedup rule). **Do not edit it.**

## Three jobs

### 1. Confirm/override the noise flag (abstract beats the keyword heuristic)
`likely_noise` was set by a crude keyword/affiliation heuristic. Using abstract + title + venue,
decide per record whether it is genuinely by our University of Utah biostatistics/epi/health
person vs a same-name author's unrelated work (materials science, engineering, pure chemistry,
etc.). DROP confirmed same-name-other-author papers (do not emit them). RESCUE any flagged record
that is actually genuine health/biostat work. Common-name authors need the most scrutiny.

### 2. Deduplicate
- **Within round 2:** a paper co-authored by two round-2 roster authors appears as two raw
  records (same openalex_id/doi, different author_slug). Collapse into ONE record whose
  `roster_authors` lists all matching round-2 slugs. Dedup key: openalex_id, then doi, then
  normalized title.
- **Cross-round:** if a round-2 paper's openalex_id or doi ALSO appears in the existing
  `papers.jsonl`, do NOT emit a duplicate and do NOT edit papers.jsonl — instead list it in your
  handback under "cross-round shared papers" (paper slug + the round-2 author slug to add).
  Claude will union the roster_authors during merge.

### 3. Classify each surviving paper — FIXED taxonomy
- `ehr_relevant` (bool): true if the paper USES electronic health record / claims / clinical
  registry data, OR develops/addresses METHODS for EHR data problems (missing data, measurement
  error, phenotyping, misclassification). Otherwise false. Keep false papers (EHR is a filter tag,
  not a gate).
- `ehr_role`: "uses-ehr" | "addresses-ehr-problem" | "na".
- `subtopics` (1-3 per paper): use ONLY these 10 locked labels — reuse them EXACTLY so nodes
  collapse:
  `clinical-application`, `causal-inference`, `survival-analysis`, `ehr-phenotyping`,
  `missing-data`, `machine-learning-prediction`, `measurement-error`,
  `treatment-effect-heterogeneity`, `sensitivity-analysis`, `bayesian-methods`.
  Do NOT add a new subtopic unless a theme genuinely recurs across multiple papers and none of
  the 10 fit — and if you do, use it sparingly and FLAG it prominently in the handback so a human
  approves it. Default hard toward reusing the 10.
- `confidence`: "high" | "medium" | "low".

## Output — write `papers-round2.jsonl` (do NOT touch papers.jsonl)
One JSON object per surviving, deduped round-2 paper, SAME contract as papers.jsonl:
`{slug, title, year, venue, doi, pmid, openalex_id, roster_authors[], abstract, ehr_relevant, ehr_role, subtopics[], confidence}`
- `slug`: `<first-roster-author-lastname>-<year>-<distinctive-word>`, kebab-case, unique. Check
  existing slugs in papers.jsonl and within papers-round2.jsonl to avoid collisions (add a numeric
  suffix if needed).
- `roster_authors`: exact author slugs from authors.yaml (round-2 authors; cross-round additions
  are handled by Claude at merge, not here).
- Keep `abstract` (stays local; dropped before publishing).

## Definition of done (run and report)
1. `python3 -c "import json;[json.loads(l) for l in open('papers-round2.jsonl')]"` — every line valid JSON.
2. Every `subtopics` value is one of the 10 locked labels (or a flagged, justified new one).
3. Every `roster_authors` slug exists in authors.yaml.
4. No slug in papers-round2.jsonl collides with a slug in papers.jsonl.
Report counts: surviving papers, dropped-as-noise (per author), within-round shared papers (with
author pairs), cross-round shared papers (paper slug + author to add), subtopic distribution, and
EHR-relevant count. Flag low-confidence records for human spot-check.

## Model/effort
Well-specified batch classification against a fixed taxonomy -> medium effort, default model.

## Handback
End with a HANDBACK block: DoD results with command output, the counts above, any new subtopic you
felt forced to add (with justification), cross-round shared papers, and low-confidence records.
