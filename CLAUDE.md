# Hundred Years' War: link-based similarity

Portfolio and learning project for Amos (data science internship search). Explain each step; plan (plan mode) before each new roadmap step. Analysis goes in Jupyter notebooks, run in VS Code with the `.venv` kernel. Keep the narrative lean: make decisions and justify them in a sentence, rather than testing every option.

This is a simplified rebuild of `~/Documents/GitHub/hundred-years-war-network` (the exploratory version, kept as an archive). Lessons from it appear here as one-line justifications.

## Roadmap
1. **Collect and explore** (`notebooks/01_collect_and_explore.ipynb`).
2. **Milne–Witten similarity** (`notebooks/02_milne_witten.ipynb`).
3. **Clustering** (`notebooks/03_clustering.ipynb`): unsupervised, on Milne–Witten similarity; metadata only describes the clusters. Evaluated by silhouette, stability and inspection, and compared with Amos's hand labels (`data/labels/hand_labels.csv`: title, label; crosstab, ARI, NMI) once he has written the codebook and labeled articles. No ML propagation of labels: comparing clusters with predicted labels would mix link structure with classifier errors.
4. **Graph and UI** (`notebooks/04_graph.ipynb` → `docs/index.html`): static page, radial view (angle = theme, radius = closeness) and network view, with an animated toggle.

## Decisions
- **Nodes (prose version, branch `prose-version`):** the seed (*Hundred Years' War*) plus every article it links to **in its body text**, excluding disambiguation pages: 276 articles. `get_link_channels` parses the seed's wikitext (mwparserfromhell; the revision current on 8 Oct 2026, matching the cached link lists) and gives each linked article one channel: prose, infobox, caption, table, reference, footnote, other template, end section (See also onward) or added by template. An article counts as prose if any of its links is in the body; quotation templates count as body. Only the nodes are filtered: similarity still uses all links (all out-links, in-links from all of Wikipedia), because in-links can't be made prose-only (1.1 million linking pages). The all-links version (789 nodes) stays on `main`.
- **All links, via the API** (`generator=links`, redirects resolved). Dropped: red links, self-links, citation identifiers (redirects named "… (identifier)"), the *Wayback Machine*.
- **`from_template`** in the links table: True when a link isn't in the article's own source text (wikitext), i.e. a navbox, sidebar or other template added it. This includes links that a citation template builds from a parameter (e.g. `author-link=John Le Patourel`); only `[[...]]` links count as written. Kept as a signal for clustering, not analyzed further. (In the exploratory version, navbox links made up 65% of network links and inflated every link measure.)
- **Milne & Witten (2008):** out-link measure (cosine of link vectors weighted log(N / df), with df counted over our articles instead of all of Wikipedia) and in-link measure (1 − Normalized Google Distance on in-links from all of Wikipedia; with only the network's in-links the formula breaks). Combined as the **average of percentile ranks**, because in-link values (median ~0.49) are ~100× larger than out-link values.
- **Clustering (Step 3):** Louvain communities (networkx) on a kNN graph (K = 10, edges weighted by Milne–Witten), seed excluded (275 articles). Metadata only *profiles* clusters: size would group by length. Not hierarchical: average linkage gives one cluster of 765 yet a higher silhouette. Cluster names are keyed by a member article (`NAMES` in the notebook), because Louvain's numbering can shift. Amos names the clusters; unnamed ones show their most central article in brackets.
- **Graph page (Step 4):** positions computed in Python (`src/layout.py`), the browser only animates between them. Radial: wedges sized by cluster and ordered by between-cluster similarity (optimal leaf ordering); radius = 0.08 + 0.92·√(rank / n), so equal-area rings hold equal numbers of articles. Color = closeness (one blue ramp), not cluster: one hue per cluster would be hard to tell apart, so themes are shown by position, labels and legend highlighting. Data in `docs/data.js` (`window.GRAPH`), not JSON, so the page works from `file://`. d3 7.9.0 from cdnjs. `docs/` is ready for GitHub Pages. Page features: multiple-choice dropdown filters (theme, closeness, links back, length, bridge; OR within a filter, AND across), a table of the 10 most related articles (to the selection, or to the seed by default; filters don't apply), seed searchable as "Hundred Years' War (Seed)", and Reset clears zoom, filters, selection and search. Counts in the page (lede, legend, rings) come from `window.GRAPH`, not hard-coded.

## Code and data
- `src/wiki.py`: API calls, cached as JSON in `data/raw/` (gitignored). `src/similarity.py`: the measures (`to_pairs` / `from_pairs`). `src/clustering.py`: `neighbors`, `knn_graph`, `louvain`, `stability`, `outside_share`. `src/layout.py`: `network_layout`, `cluster_order`, `radial_layout`.
- `docs/`: `index.html` (the page, d3) and `data.js` (written by notebook 04; regenerate after changing clusters).
- `data/processed/`: Parquet tables (committed) and CSV copies without the text column (gitignored, written by the notebooks):
  - `articles` (one row per article: title, pageid, is_seed, shortdesc, first_paragraph, word_count, n_links_out, out_degree, pct_out_degree, in_degree, links_to_seed, text)
  - `links` (source, target, target_in_network, from_template = whether the source's link to the target came from a template)
  - `seed_links` (target, channel, is_node: one row per article the seed links to, disambiguation pages excluded)
  - `pairs` (a, b, outlink, inlink, milne_witten; one row per pair, seed included) and `seed_similarity` (each article's three scores and ranks vs the seed)
  - `clusters` (title, cluster, cluster_name, centrality = mean similarity within the cluster, outside_share = share of the 10 nearest articles in other clusters; one row per article, seed excluded)
- `data/raw/`: `links/`, `articles/`, `backlinks/` (copied from the archive repo; collected 29 Sep – 6 Oct 2026), `written_links/` (8 Oct 2026), `link_channels/` (the seed only, from its 30 Sep 2026 revision), `_article_count.json` (W = 7,248,637).

## Findings so far
Prose version (branch `prose-version`):
- **Step 1:** of the seed's 788 linked articles, 275 are linked from prose, 452 only by templates, 29 only in end sections, 15 captions, 10 infobox, 4 references, 3 tables. 276 nodes, 7,376 network links, density 0.097, reciprocity 0.58, one component; 59% link back to the seed. Templates add 54% of all links but only 28% of network links (69% with every linked article).
- **Step 2:** in-link top 10 = the war's core as before; out-link top 10 = the war's phases, Siege of Orléans, Battle of Patay. Spearman out-link vs in-link 0.55 (0.42 before); the rank average correlates 0.88 with each. Kingdom of England 38th, Artillery 239th of 275.
- **Step 3:** 8 Louvain clusters (14–56 articles), not yet named. Less stable: ARI 0.78 across seeds (always 8), 0.64 on 80% subsets; K = 5 → 11 clusters (ARI 0.56), K = 15 → 6 (0.63). Silhouette 0.19 (average linkage 0.23 with 267 of 275 in one cluster). Median seed rank per cluster 54–229.

All-links version (`main`):
- **Step 1:** 789 nodes, 48,006 network links, density 0.077, reciprocity 0.70, one connected component; 66% of 1-hop articles link back to the seed. Templates add 58% of all links and 69% of network links (57% of the seed's).
- **Step 2:** in-link top 10 for the seed = the war's core (Edward III, Charles VII, Henry V, Poitiers, Crécy, Agincourt, Black Death); out-link top 10 = navbox groups (war phases, 1429 Loire campaign). Out-link vs in-link Spearman 0.42; the rank average correlates 0.83 / 0.84 with each. Crécy–seed: in-link 0.755 (|A| = 518, |B| = 2,752, shared 266). Kingdom of England ranks 133rd, Norfolk Record Office 755th. Template-linked articles score higher on all three measures (Milne–Witten 0.84 vs 0.75).
- **Step 3:** 12 Louvain clusters. Stability: ARI 0.89 across seeds (11–13 clusters), 0.79 on 80% subsets, 0.77 for K = 15 (K = 5 gives 16 clusters). Silhouette 0.21 (average linkage, 5 clusters: 0.28 with 765 articles in one). Closest themes to the seed (median rank ~230–260): Lancastrian phase, medieval society, Joan of Arc; farthest: Edwardian phase (short articles plus absorbed publishers), towns, war in general. Template share ranges 0–94% (medieval society 94% = navbox echo; monarchies and towns 0–22%). Bridges: Battle of Jargeau (Lancastrian ↔ Joan of Arc), Feudalism, Kingdom of France.

## To discuss later
Remind Amos to raise this when presenting or discussing the project, and to add it to the README / write-up.
- **Links reach an article through many channels:** prose written by the editor, navboxes, sidebars, infoboxes, citations and further reading. Only some of these mean the articles are closely related.
- **`from_template` is only a rough hint, and can mislead.** It's computed here (the API's full link list minus the `[[...]]` links in the wikitext), not given by the API. It records how a link was *written*, not where it sits on the page. Example from the seed's Further reading, one book entry: the publisher `publisher=[[Robinson Publishing|Robinson]]` (a redirect to *Constable & Robinson*) is False, while the author `author-link=Desmond Seward` is True. *John Le Patourel* (bibliography, `author-link=`) is True.
- **Hence measures that don't rely on how a link was written:** Milne–Witten similarity (out-links and in-links from all of Wikipedia) and clustering on it, rather than trusting any single link flag. Templates add 58% of all links and 69% of network links, so this matters for every link measure.
- **Relatedness vs similarity, the motivation for links:** Milne & Witten measure *relatedness* (connected: Battle of Crécy ~ Edward III), not *similarity* (same kind: Battle of Crécy ~ Battle of Gettysburg). Editors link what's connected, so links encode relatedness; text (TF-IDF, embeddings) mostly encodes similarity, so text clusters group by article type and link clusters by theme or episode. Type-based hand labels may therefore match link clusters poorly without either being wrong. Text-based similarity is future work.

## Gotchas
- **Data collected on different days:** link lists (29 Sep) and written links (8 Oct) can disagree when a page changed in between; get_written_links matches against the cached link titles first, which absorbs page renames.
- **Pagination:** 500 results per response plus a `continue` token; a page can appear in two batches, so `_query_all` merges by title.
- **Rate limits:** HTTP 429 → `_api_get` waits and retries, as for `maxlag`.
- **Citation identifiers** arrive already resolved (e.g. *Digital object identifier*), so they're recognized by the redirect's original name.
- **The API User-Agent** carries the GitHub URL. Never an email address: the repo will be public.

## Environment
- Python 3.14 in `.venv`; `.venv/bin/pip install -r requirements.txt`.
- Public at github.com/amos-johnson/hundred-years-war-similarity; GitHub Pages serves `docs/` at https://amos-johnson.github.io/hundred-years-war-similarity/. Commits use the GitHub noreply email (repo-local `user.email`), never the personal one.
- Commits end with the Co-Authored-By line that Claude Code specifies.
