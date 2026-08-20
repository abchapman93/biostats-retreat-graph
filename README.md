# Biostatistics Retreat Graph

A self-contained, presentation-oriented visualization of University of Utah
Biostatistics authors, their publications, and EHR-relevant research subtopics.

Live site: <https://abchapman93.github.io/biostats-retreat-graph/>.

The default view keeps the graph readable for a retreat presentation:

- red circles in the upper semicircle are faculty authors;
- unfilled, light-red-outlined circles in the lower semicircle are student and postdoctoral authors; and
- soft-blue circles in the center are subtopics.

Click an author to expand that author's publications. Each publication remains connected to every division coauthor,
but is positioned around one primary display author. Click a publication to see
its metadata and its subtopic links. The **EHR-focused only** control filters
the view to EHR-relevant publications and their connected authors/subtopics.

## Run locally

The viewer has no backend or external dependencies. Open `index.html` directly,
or serve this directory for the most browser-consistent preview:

```bash
python3 -m http.server 8793
```

Then open <http://127.0.0.1:8793>.

## Data and rebuilds

`papers.jsonl` and `authors.yaml` are the source data. Rebuild the static graph
after an intentional source-data update:

```bash
python3 build_graph.py
```

This overwrites `graph-data.js`, which is loaded locally by `index.html`.
`raw-candidate-topics.jsonl` contains row-aligned topic assignments for
`raw-candidates.jsonl`. All candidates not marked `likely_noise` have been
promoted into `papers.jsonl`; the flagged records remain excluded.
Publication metadata carries a `primary_author` display anchor. The current
source retains ordered division coauthors but not publication-wide first/senior
author positions, so roster order is used as the deterministic fallback.
