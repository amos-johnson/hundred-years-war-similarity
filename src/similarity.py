"""Milne & Witten's (2008) link-based similarity between articles.

Each measure returns a symmetric DataFrame, with article titles as index and
columns, values from 0 (nothing in common) to 1, and 1 on the diagonal:

    outlink_similarity(links, titles)         -> similarity of the articles' out-links
    inlink_similarity(backlinks, W, titles)   -> similarity of the articles' in-links
    rank_average(*measures)                   -> average of the measures' percentile ranks

to_pairs(measures) turns these tables into one row per article pair.

The measures use one trick: a sparse 0/1 matrix X with one row per article
and one column per linked (or linking) page. X @ X.T then counts, for every
pair of articles at once, how many pages they have in common.
"""

import numpy as np
import pandas as pd
from scipy import sparse


def _matrix(pairs, titles):
    """Sparse 0/1 matrix from (article, page) pairs: one row per title, one column per page."""
    pairs = pairs[pairs.iloc[:, 0].isin(titles)]
    row_of = {t: i for i, t in enumerate(titles)}
    pages, cols = np.unique(pairs.iloc[:, 1].to_numpy(), return_inverse=True)
    rows = pairs.iloc[:, 0].map(row_of).to_numpy()
    return sparse.csr_matrix((np.ones(len(pairs)), (rows, cols)), shape=(len(titles), len(pages)))


def _finish(values, titles):
    """Clean up a similarity matrix: symmetric, 0 to 1, 1 on the diagonal."""
    values = np.clip((values + values.T) / 2, 0, 1)
    np.fill_diagonal(values, 1)
    return pd.DataFrame(values, index=titles, columns=titles)


def outlink_similarity(links, titles):
    """Milne & Witten's out-link measure: cosine similarity of weighted link vectors.

    Each article is a vector over the pages it links to. A link to page t gets
    the weight log(N / df_t), where df_t is how many of the N articles link to t,
    so a link that many articles share (e.g. to "England") counts for little and
    a rare one counts for a lot. This is TF-IDF applied to links.

    Approximation: the paper uses log(|W| / |T|), with |T| = the articles in all
    of Wikipedia that link to t. We use the N articles in our network instead,
    which avoids looking up the in-links of every one of ~110k link targets.

    `links` has columns source and target.
    """
    X = _matrix(links[["source", "target"]], titles)
    df = np.asarray(X.sum(axis=0)).ravel()
    weights = np.log(len(titles) / df)
    Xw = sparse.csr_matrix(X.multiply(weights))
    dot = (Xw @ Xw.T).toarray()
    norm = np.sqrt(np.diag(dot))
    with np.errstate(divide="ignore", invalid="ignore"):
        values = np.where(np.outer(norm, norm) > 0, dot / np.outer(norm, norm), 0.0)
    return _finish(values, titles)


def inlink_similarity(backlinks, W, titles):
    """Milne & Witten's in-link measure: 1 − Normalized Google Distance.

    A and B are the sets of articles that link to a and b (from all of
    Wikipedia), and W is the number of articles in Wikipedia:

        distance = (log max(|A|,|B|) − log |A ∩ B|) / (log W − log min(|A|,|B|))

    The numerator is how far the overlap falls short of the more popular
    article; the denominator is how rare the less popular one is overall.
    Pairs with no shared in-links get 0; distances above 1 are clipped to 0.

    `backlinks` maps each title to the list of articles that link to it.
    """
    pairs = pd.DataFrame([(t, s) for t in titles for s in backlinks[t]], columns=["article", "linked_from"])
    X = _matrix(pairs, titles)
    shared = (X @ X.T).toarray()
    size = np.asarray(X.sum(axis=1)).ravel()
    larger = np.maximum(size[:, None], size[None, :])
    smaller = np.minimum(size[:, None], size[None, :])
    with np.errstate(divide="ignore", invalid="ignore"):
        distance = (np.log(larger) - np.log(shared)) / (np.log(W) - np.log(smaller))
        values = np.where(shared > 0, 1 - distance, 0.0)
    return _finish(values, titles)


def rank_average(*measures):
    """Average of the measures' percentile ranks over all article pairs.

    Each measure is first turned into percentile ranks (0 = the least similar
    pair, 1 = the most similar), so measures on different scales count equally.
    """
    titles = list(measures[0].index)
    i, j = np.triu_indices(len(titles), k=1)
    ranks = [pd.Series(m.loc[titles, titles].to_numpy()[i, j]).rank(pct=True).to_numpy() for m in measures]
    values = np.zeros((len(titles), len(titles)))
    values[i, j] = np.mean(ranks, axis=0)
    return _finish(values + values.T, titles)


def to_pairs(measures):
    """One row per article pair (a, b with a before b), one column per measure.

    `measures` maps a column name to a similarity DataFrame from this module.
    """
    first = next(iter(measures.values()))
    titles = first.index.to_numpy()
    i, j = np.triu_indices(len(titles), k=1)
    table = pd.DataFrame({"a": titles[i], "b": titles[j]})
    for name, matrix in measures.items():
        table[name] = matrix.loc[titles, titles].to_numpy()[i, j]
    return table
