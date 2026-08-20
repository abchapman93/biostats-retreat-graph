# Dan's topic -> author links (source: "EHR/Causal" retreat slide, 2026-08-20)

Raw person-topic mapping straight off Dan's slide, kept here so a future session can
implement it as **direct** person->topic graph links. Today the graph only connects an
author to a topic indirectly, through a paper both are tagged on (see `build_graph.py`
CURATED_TOPICS / the render logic in `index.html` that derives author-topic edges from
shared papers) — there's no direct person->concept edge type yet.

| Slide topic (as written) | People listed | Resolved author slug(s) |
|---|---|---|
| Target Trial Emulation/Causal Effect Estimation | Alec, Dan, Tom, Jincheng, Crystal, Ravi, Eric, Daniel, Michael, Jennifer, Xuan | `alec-chapman`, `daniel-scharfstein`, `jincheng-shen`, `yizhe-crystal-xu`, `ravinder-singh`, `xuan-wang` (Tom/Eric/Daniel/Michael/Jennifer unresolved, see `PENDING-AUTHORS.md`) |
| Dynamic Treatment Regimes | Jincheng, Alec, Dan | `jincheng-shen`, `alec-chapman`, `daniel-scharfstein` |
| Federated/Transfer Learning | Xuan | `xuan-wang` |
| Missing Data | Dan, Yidan, Yongjun, Jennifer | `daniel-scharfstein`, `yidan-zhang`, `yongjun-lee` (Jennifer unresolved) |
| Informative Data Collection | Dan | `daniel-scharfstein` |
| Prediction | Bernardo, Xuan, Julia | `bernardo-modenesi`, `xuan-wang`, `julia-bohman` |
| Latent Trajectories | Yizhen | `yizhen-xu` |
| Survival Analysis | Xuan, Dan, Julia | `xuan-wang`, `daniel-scharfstein`, `julia-bohman` |
| Confounding | Dan, Bernardo | `daniel-scharfstein`, `bernardo-modenesi` |
| Treatment Effect Heterogeneity | Jincheng, Crystal | `jincheng-shen`, `yizhe-crystal-xu` |

"Dan" is assumed to be `daniel-scharfstein` throughout (matches his registered alias
"Dan Scharfstein").

## Topic taxonomy has since been merged (2026-08-20 pass)

The slide's 10 topics no longer map 1:1 to graph subtopic nodes. When wiring up direct
links, use these merged labels (current `CURATED_TOPICS` in `build_graph.py`), not the
original slide names:

- "Target Trial Emulation/Causal Effect Estimation" merged with the auto-generated
  `causal-inference` subtopic -> **"Target trial emulation & causal inference"**
- "Missing Data" and "Informative Data Collection" merged into one node, despite being
  listed separately on the slide -> **"Missing & informative data"**
- "Prediction" merged with the auto-generated `machine-learning-prediction` subtopic ->
  **"Prediction"** (label unchanged)
- All other slide topics kept a 1:1 node, just recased to a clean label (e.g.
  "Dynamic Treatment Regimes" -> "Dynamic treatment regimes").
