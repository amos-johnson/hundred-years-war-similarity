# Hundred Years' War: link-based similarity

Which Wikipedia articles are most closely related to the [Hundred Years' War](https://en.wikipedia.org/wiki/Hundred_Years%27_War), and how do they group together? This project measures the similarity between the articles the war's page links to, using **Milne & Witten's (2008) link-based measures**, and then clusters them.

*Work in progress.*

## Approach

1. **Collect and explore** (`notebooks/01_collect_and_explore.ipynb`). The seed article and every article it links to (789 articles), their links, text and short descriptions, from the Wikipedia API. Each link is flagged if it comes from a template (navbox, sidebar) rather than the article's own text.
2. **Milne–Witten similarity** (`notebooks/02_milne_witten.ipynb`). Every pair of articles is compared by the pages they link to (out-links) and the pages that link to them (in-links, from all of Wikipedia). The two are combined by averaging their percentile ranks, because they're on very different scales.
3. **Clustering** (`notebooks/03_clustering.ipynb`). Louvain communities on a graph that joins each article to its 10 most similar articles. The result is 12 stable themes (the war's phases, Joan of Arc, the two monarchies, Burgundy, the Middle Ages and more), profiled by how close each is to the war and how much of it comes from templates.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

The notebooks call the Wikipedia API on the first run (about 2 hours in total, mostly in-links) and cache the responses in `data/raw/`.

## Reference

Milne, D. & Witten, I. H. (2008). *An effective, low-cost measure of semantic relatedness obtained from Wikipedia links.* AAAI Workshop on Wikipedia and Artificial Intelligence.
