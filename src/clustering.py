"""Clustering articles by their similarity, as communities in a neighbor graph.

`similarity` is always a square DataFrame from similarity.py (titles as index
and columns, 1 on the diagonal):

    neighbors(similarity, k)                -> each article's k most similar articles (positions)
    knn_graph(similarity, k)                -> graph joining each article to its k most similar
    louvain(graph, seed)                    -> cluster label for each article
    stability(similarity, labels, k, ...)   -> agreement with clusterings of random subsets
    outside_share(similarity, labels, k)    -> share of each article's neighbors in other clusters

Why a neighbor graph: almost every pair of articles has some similarity, so a
graph with all pairs as edges is one dense ball. Keeping each article's k
strongest links leaves the structure that matters.
"""

import networkx as nx
import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score


def neighbors(similarity, k):
    """For each article, the positions of its k most similar other articles."""
    values = similarity.to_numpy().copy()
    np.fill_diagonal(values, -np.inf)
    return np.argsort(-values, axis=1)[:, :k]


def knn_graph(similarity, k):
    """Undirected graph with an edge from each article to its k most similar articles.

    Edges are weighted by similarity. An edge kept by either article stays, so
    some articles end up with more than k edges.
    """
    titles = similarity.index.to_numpy()
    values = similarity.to_numpy()
    graph = nx.Graph()
    graph.add_nodes_from(titles)
    for i, row in enumerate(neighbors(similarity, k)):
        for j in row:
            graph.add_edge(titles[i], titles[j], weight=values[i, j])
    return graph


def louvain(graph, seed=0, resolution=1.0):
    """Louvain communities, as a Series of labels (0 = the largest cluster) indexed by title.

    Louvain moves nodes between groups to maximize modularity: how much more
    edge weight falls inside groups than expected if edges were placed at
    random. It picks the number of groups itself. It starts from a random
    order, hence the seed.
    """
    communities = nx.community.louvain_communities(graph, weight="weight", resolution=resolution, seed=seed)
    communities = sorted(communities, key=len, reverse=True)
    labels = {title: c for c, members in enumerate(communities) for title in members}
    return pd.Series(labels, name="cluster").sort_index()


def stability(similarity, labels, k, n_runs=20, frac=0.8, seed=0):
    """Adjusted Rand index between `labels` and clusterings of random subsets of the articles.

    Each run drops a random (1 − frac) of the articles, rebuilds the graph and
    reclusters, then compares the labels of the articles both share. ARI is 1
    for the same grouping and about 0 for one no better than chance.
    """
    rng = np.random.default_rng(seed)
    scores = []
    for run in range(n_runs):
        keep = rng.choice(similarity.index, size=int(frac * len(similarity)), replace=False)
        sub = louvain(knn_graph(similarity.loc[keep, keep], k), seed=run)
        scores.append(adjusted_rand_score(labels[sub.index], sub))
    return np.array(scores)


def outside_share(similarity, labels, k):
    """Share of each article's k most similar articles that sit in another cluster.

    High values mark bridge articles, pulled between two or more themes.
    """
    titles = similarity.index
    own = labels[titles].to_numpy()
    neighbor_labels = own[neighbors(similarity, k)]
    return pd.Series((neighbor_labels != own[:, None]).mean(axis=1), index=titles, name="outside_share")
