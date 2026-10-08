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
- `data/processed/`: Parquet tables (committed) and CSV copies without the text column (gitignored, written by the notebooks).

## Gotchas
- **Pagination:** 500 results per response plus a `continue` token; a page can appear in two batches, so `_query_all` merges by title.
- **Rate limits:** HTTP 429 → `_api_get` waits and retries, as for `maxlag`.
- **Citation identifiers** arrive already resolved (e.g. *Digital object identifier*), so they're recognized by the redirect's original name.
- **The API User-Agent** carries the GitHub URL. Never an email address: the repo will be public.

## Environment
- Python 3.14 in `.venv`; `.venv/bin/pip install -r requirements.txt`.
- Local only for now (planned for github.com/amos-johnson).
- Commits end with the Co-Authored-By line that Claude Code specifies.
