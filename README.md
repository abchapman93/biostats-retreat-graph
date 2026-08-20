# Biostatistics Retreat Graph

A self-contained, presentation-oriented visualization of University of Utah
Biostatistics authors, their publications, and EHR-relevant research subtopics.

The default view keeps the graph readable for a retreat presentation:

- red circles are authors;
- white circles show each author's publication count; and
- soft-blue circles in the center are subtopics.

Click an author or its publication-count circle to expand that author's
publications. Each publication remains connected to every division coauthor,
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
Publication metadata carries a `primary_author` display anchor. The current
source retains ordered division coauthors but not publication-wide first/senior
author positions, so roster order is used as the deterministic fallback.
