# Hundred Years' War: link-based similarity

Which Wikipedia articles are most closely related to the [Hundred Years' War](https://en.wikipedia.org/wiki/Hundred_Years%27_War), and how do they group together? This project collects the 275 articles the war's page links to in its body text, measures how similar every pair is from their links (**Milne & Witten, 2008**), clusters them into themes and publishes the result as an interactive graph.

**[▶ Open the interactive graph](https://amos-johnson.github.io/hundred-years-war-similarity/)**

[![The radial view: the war at the center, one wedge per theme, each article placed by its closeness to the war](docs/preview.png)](https://amos-johnson.github.io/hundred-years-war-similarity/)

## Results

*This branch is being rebuilt on articles linked from the war's body text only (275 of the 788 linked articles). The themes will be named and the findings written up next.*

- **Most links don't come from the body text.** Of the 788 articles the war's page links to, 452 are linked only by templates (navboxes, sidebars, hatnotes) and 61 only by the infobox, captions, tables, citations or end sections. Keeping the 275 prose-linked articles cuts the share of template links between articles from 69% to 28%.
- **8 themes**, less stable than with every linked article: adjusted Rand index 0.78 across random seeds (0.89 before) and 0.64 when 20% of the articles are dropped.
- **The two halves of the measure capture different things.**
  - In-links (which pages link to both articles) find the war's core: Edward III, Charles VII, Henry V, Crécy, Agincourt.
  - Out-links (which pages both articles link to) find articles with overlapping link lists, such as the war's phases.
  - Spearman correlation between the two: 0.55.

## Approach

| Step | Notebook | What it does |
|---|---|---|
| 1. Collect and explore | [`01_collect_and_explore`](notebooks/01_collect_and_explore.ipynb) | The seed article and every article it links to in its body text, from the Wikipedia API: links (with redirects resolved), text and short descriptions. The seed's links are sorted by where they sit on the page (prose, infobox, captions, references, end sections, templates); only prose-linked articles are kept. |
| 2. Similarity | [`02_milne_witten`](notebooks/02_milne_witten.ipynb) | Every pair of articles compared by the pages they link to (out-links, TF-IDF-style weighted cosine) and the pages that link to them (in-links from all 7.2 million English Wikipedia articles, Normalized Google Distance). The two are combined by averaging percentile ranks, because their scales differ by about 100×. |
| 3. Clustering | [`03_clustering`](notebooks/03_clustering.ipynb) | Louvain communities on a graph joining each article to its 10 most similar articles. Evaluated by silhouette, stability (seeds, subsamples, neighborhood size) and inspection; profiled with metadata. |
| 4. Interactive graph | [`04_graph`](notebooks/04_graph.ipynb) | Radial and force-directed layouts computed in Python, exported to a static d3 page with filters, search and a table of related articles. |

**Tools:** Python, pandas, NumPy, SciPy (sparse matrices, hierarchical clustering), scikit-learn, NetworkX, matplotlib, d3.js, the MediaWiki API.

## Repository layout

```
src/
  wiki.py          Wikipedia API calls, cached as JSON
  similarity.py    Milne–Witten measures
  clustering.py    neighbor graph, Louvain, stability
  layout.py        radial and network layouts
notebooks/         the four steps above, with outputs
data/processed/    Parquet tables: articles, links, seed_links, pairs, seed_similarity, clusters
docs/              the interactive page (served by GitHub Pages)
```

## Run it locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

- **Notebooks 03 and 04** run from the committed tables in `data/processed/`.
- **Notebooks 01 and 02** call the Wikipedia API on the first run. That takes about 2 hours, mostly in-links. They cache the responses in `data/raw/`, which isn't committed.
- **To open the graph locally,** double-click `docs/index.html`. Or, from the repo folder, run `python -m http.server -d docs` and go to http://localhost:8000.

## Reference

Milne, D. & Witten, I. H. (2008). *An effective, low-cost measure of semantic relatedness obtained from Wikipedia links.* AAAI Workshop on Wikipedia and Artificial Intelligence.
