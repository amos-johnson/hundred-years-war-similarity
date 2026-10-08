# Hundred Years' War: link-based similarity

Portfolio and learning project for Amos (data science internship search). Explain each step; plan (plan mode) before each new roadmap step. Analysis goes in Jupyter notebooks, run in VS Code with the `.venv` kernel. Keep the narrative lean: make decisions and justify them in a sentence, rather than testing every option.

This is a simplified rebuild of `~/Documents/GitHub/hundred-years-war-network` (the exploratory version, kept as an archive). Lessons from it appear here as one-line justifications.

## Roadmap
1. **Collect and explore** (`notebooks/01_collect_and_explore.ipynb`).
2. **Milne–Witten similarity** (`notebooks/02_milne_witten.ipynb`).
3. **Clustering:** unsupervised, on the similarity scores plus article metadata; evaluated by silhouette, stability and inspection. No hand labels: labels of relatedness to the seed would make a classifier seed-specific, and every article was selected by the seed's links (selection bias).
4. **Graph and UI:** an interactive graph of the clusters (later).

## Decisions
- **Nodes:** the seed (*Hundred Years' War*) plus every article it links to, excluding disambiguation pages: 789 articles.
- **All links, via the API** (`generator=links`, redirects resolved). Dropped: red links, self-links, citation identifiers (redirects named "… (identifier)"), the *Wayback Machine*.
- **`from_template`** in the links table: True when a link isn't in the article's own source text (wikitext), i.e. a navbox, sidebar or other template added it. Kept as a signal for clustering, not analyzed further. (In the exploratory version, navbox links made up 65% of network links and inflated every link measure.)
- **Milne & Witten (2008):** out-link measure (cosine of link vectors weighted log(N / df), with df counted over our 789 articles instead of all of Wikipedia) and in-link measure (1 − Normalized Google Distance on in-links from all of Wikipedia; with only the network's in-links the formula breaks). Combined as the **average of percentile ranks**, because in-link values (median ~0.49) are ~100× larger than out-link values.

## Code and data
- `src/wiki.py`: API calls, cached as JSON in `data/raw/` (gitignored). `src/similarity.py`: the measures.
- `data/processed/`: Parquet tables (committed) and CSV copies without the text column (gitignored, written by the notebooks):
  - `articles` (one row per article: title, pageid, is_seed, shortdesc, first_paragraph, word_count, n_links_out, out_degree, pct_out_degree, in_degree, links_to_seed, text)
  - `links` (source, target, target_in_network, from_template)
  - `pairs` (a, b, outlink, inlink, milne_witten; 310,866 rows) and `seed_similarity` (each article's three scores and ranks vs the seed)
- `data/raw/`: `links/`, `articles/`, `backlinks/` (copied from the archive repo; collected 29 Sep – 6 Oct 2026), `written_links/` (8 Oct 2026), `_article_count.json` (W = 7,248,637).

## Findings so far
- **Step 1:** 789 nodes, 48,006 network links, density 0.077, reciprocity 0.70, one connected component; 66% of 1-hop articles link back to the seed. Templates add 58% of all links and 69% of network links (57% of the seed's).
- **Step 2:** in-link top 10 for the seed = the war's core (Edward III, Charles VII, Henry V, Poitiers, Crécy, Agincourt, Black Death); out-link top 10 = navbox groups (war phases, 1429 Loire campaign). Out-link vs in-link Spearman 0.42; the rank average correlates 0.83 / 0.84 with each. Crécy–seed: in-link 0.755 (|A| = 518, |B| = 2,752, shared 266). Kingdom of England ranks 133rd, Norfolk Record Office 755th.

## Gotchas
- **Data collected on different days:** link lists (29 Sep) and written links (8 Oct) can disagree when a page changed in between; get_written_links matches against the cached link titles first, which absorbs page renames.
- **Pagination:** 500 results per response plus a `continue` token; a page can appear in two batches, so `_query_all` merges by title.
- **Rate limits:** HTTP 429 → `_api_get` waits and retries, as for `maxlag`.
- **Citation identifiers** arrive already resolved (e.g. *Digital object identifier*), so they're recognized by the redirect's original name.
- **The API User-Agent** carries the GitHub URL. Never an email address: the repo will be public.

## Environment
- Python 3.14 in `.venv`; `.venv/bin/pip install -r requirements.txt`.
- Local only for now (planned for github.com/amos-johnson).
- Commits end with the Co-Authored-By line that Claude Code specifies.
