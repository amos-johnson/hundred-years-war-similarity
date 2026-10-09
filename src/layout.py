"""Positions for drawing the articles: x and y from -1 to 1 for each one.

    network_layout(graph)                         -> force layout: similar articles pulled together
    cluster_order(similarity, labels)             -> order of the clusters around a circle
    radial_layout(labels, seed_rank, order)       -> seed at the center, one wedge per cluster

In the radial layout an article's angle shows its cluster (theme) and its
distance from the center its rank in similarity to the seed (closeness).
"""

import networkx as nx
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import leaves_list, linkage, optimal_leaf_ordering
from scipy.spatial.distance import squareform

GOLDEN = (np.sqrt(5) - 1) / 2  # spreads a sequence evenly over [0, 1) without repeats


def network_layout(graph, seed=0):
    """Force-directed layout: each edge a spring as strong as its weight; all nodes repel.

    Returns a DataFrame with columns x and y, indexed by node.
    """
    pos = nx.spring_layout(graph, weight="weight", seed=seed)
    xy = pd.DataFrame(pos, index=["x", "y"]).T
    return xy / np.abs(xy.to_numpy()).max()


def cluster_order(similarity, labels):
    """Clusters in an order that puts similar ones side by side.

    Two clusters' similarity is the mean similarity between their articles.
    Hierarchical clustering of the clusters, with the leaves reordered so that
    neighbors in the order are as similar as possible (optimal leaf ordering).
    """
    clusters = sorted(labels.unique())
    titles = similarity.index
    own = labels[titles].to_numpy()
    values = similarity.to_numpy()
    between = np.array([[values[np.ix_(own == a, own == b)].mean() for b in clusters] for a in clusters])
    distance = squareform(1 - between, checks=False)
    tree = optimal_leaf_ordering(linkage(distance, "average"), distance)
    return [clusters[i] for i in leaves_list(tree)]


def radial_layout(labels, seed_rank, order, gap=0.04, inner=0.08):
    """Seed at (0, 0); each cluster a wedge, sized by its number of articles.

    Radius = inner + (1 − inner) · √(rank / n), with rank 1 = most similar to
    the seed. The square root gives every ring of equal area the same number
    of articles. `gap` is the empty angle between wedges, in radians; `inner`
    keeps room for the seed.

    Within a wedge, articles sorted by rank take the angles k · GOLDEN (mod 1)
    of the wedge's width, so articles of neighboring rank land far apart.
    Returns (positions, wedges): x, y per article, and each cluster's
    start and end angle.
    """
    n = len(labels)
    sizes = labels.value_counts()
    usable = 2 * np.pi - gap * len(order)
    rows, wedges, start = [], {}, 0.0
    for c in order:
        width = usable * sizes[c] / n
        members = seed_rank[labels.index[labels == c]].sort_values()
        for k, (title, rank) in enumerate(members.items(), start=1):
            angle = start + width * ((k * GOLDEN) % 1)
            radius = inner + (1 - inner) * np.sqrt(rank / n)
            rows.append((title, radius * np.cos(angle), radius * np.sin(angle)))
        wedges[c] = (start, start + width)
        start += width + gap
    positions = pd.DataFrame(rows, columns=["title", "x", "y"]).set_index("title")
    return positions.loc[labels.index], wedges
