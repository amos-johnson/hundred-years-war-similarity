"""Get Wikipedia articles' links, text and in-links from the MediaWiki API.

    get_links(title)          -> the articles `title` links to, redirects resolved
    get_written_links(title)  -> the ones written in its own source text (not added by templates)
    get_article(title)        -> its page ID, short description and plain text
    get_backlinks(title)      -> the articles that link to `title`, from all of Wikipedia
    get_article_count()       -> how many articles English Wikipedia has

Results are cached as JSON in data/raw/, so re-runs don't hit the network.
"""

import json
import re
import time
from pathlib import Path

import requests

API_URL = "https://en.wikipedia.org/w/api.php"
# Wikimedia asks API clients to identify themselves with a descriptive User-Agent.
USER_AGENT = "hundred-years-war-similarity/0.1 (https://github.com/amos-johnson)"
CACHE_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

# Citation links that appear on many articles but say nothing about the topic.
EXCLUDED_TITLES = {"Wayback Machine"}

# Article text is cut at the first of these section headings.
END_SECTIONS = "See also|Notes|References|Citations|Sources|Bibliography|Further reading|External links"

_session = requests.Session()
_session.headers["User-Agent"] = USER_AGENT


def _api_get(params, pause=0.1, retries=5):
    """Call the API, pausing briefly afterward to be polite.

    If the servers are busy (a "maxlag" error) or we're sending requests too
    fast (HTTP 429), wait and try again.
    """
    params = {"format": "json", "formatversion": 2, "maxlag": 5, **params}
    for attempt in range(1, retries + 1):
        resp = _session.get(API_URL, params=params, timeout=30)
        if resp.status_code == 429:
            # Wait as long as the server asks (Retry-After, in seconds), or longer each time.
            retry_after = resp.headers.get("Retry-After", "")
            time.sleep(float(retry_after) if retry_after.isdigit() else 10 * attempt)
            continue
        resp.raise_for_status()
        time.sleep(pause)
        data = resp.json()
        if data.get("error", {}).get("code") == "maxlag":
            time.sleep(5 * attempt)
            continue
        if "error" in data:
            raise RuntimeError(f"API error: {data['error']}")
        return data
    raise RuntimeError("API still busy after retries")


def _query_all(params):
    """Run a query, following `continue` tokens until all results are in.

    Returns ({title: page}, [redirects]). A page can appear in more than one
    batch, so batches are merged by title.
    """
    pages, redirects, cont = {}, [], {}
    while True:
        data = _api_get({"action": "query", **params, **cont})
        query = data.get("query", {})
        for page in query.get("pages", []):
            pages.setdefault(page["title"], {}).update(page)
        redirects += query.get("redirects", [])
        if "continue" not in data:
            return pages, redirects
        cont = data["continue"]


def _cache_path(folder, title):
    safe = re.sub(r"[^\w\-]+", "_", title).strip("_")
    return CACHE_DIR / folder / f"{safe}.json"


def _save(path, result):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result))


def get_links(title):
    """Articles that `title` links to, as {title: {pageid, shortdesc, disambiguation}}.

    Redirects are resolved to canonical titles. Red links, citation links such
    as "Doi (identifier)" and EXCLUDED_TITLES, and links back to the page
    itself are dropped.
    """
    path = _cache_path("links", title)
    if path.exists():
        return json.loads(path.read_text())

    pages, redirects = _query_all({
        "titles": title,
        "generator": "links",    # the pages `title` links to...
        "gplnamespace": 0,       # ...that are articles (not File:, Category:, ...)
        "gpllimit": "max",       # 500 per request
        "redirects": 1,          # under their canonical titles
        "prop": "pageprops",
        "ppprop": "disambiguation|wikibase-shortdesc",
    })
    identifiers = {r["to"] for r in redirects if r["from"].endswith("(identifier)")}
    excluded = identifiers | EXCLUDED_TITLES
    links = {
        t: {
            "pageid": p["pageid"],
            "shortdesc": p.get("pageprops", {}).get("wikibase-shortdesc"),
            "disambiguation": "disambiguation" in p.get("pageprops", {}),
        }
        for t, p in pages.items()
        if "pageid" in p and t not in excluded and t != title
    }
    _save(path, links)
    return links


def get_written_links(title):
    """Articles linked in `title`'s own source text (its wikitext), as a sorted list.

    get_links() also returns links that templates add when the page is
    displayed, such as navboxes and sidebars. A link that is in get_links()
    but not here came from a template. Links written as [[...]] inside
    citations or infobox fields count as written; links a template builds
    from a parameter (e.g. a citation's author-link=) don't. Titles are
    resolved to match get_links().
    """
    path = _cache_path("written_links", title)
    if path.exists():
        return json.loads(path.read_text())

    page = _api_get({"action": "query", "titles": title, "prop": "revisions",
                     "rvprop": "content", "rvslots": "main"})["query"]["pages"][0]
    wikitext = page["revisions"][0]["slots"]["main"]["content"]

    # A wiki link is [[Target]] or [[Target|shown text]]; drop any #section part.
    targets = set()
    for target in re.findall(r"\[\[([^\[\]|]+)", wikitext):
        target = target.split("#")[0].replace("_", " ").strip().lstrip(":")
        if target:
            targets.add(target[0].upper() + target[1:])

    # Most targets already match a title from get_links(). Look up the rest
    # (redirects and other spellings), 50 titles per request.
    canonical = {t: t for t in targets if t in get_links(title)}
    unknown = sorted(targets - set(canonical))
    for i in range(0, len(unknown), 50):
        batch = unknown[i:i + 50]
        query = _api_get({"action": "query", "titles": "|".join(batch), "redirects": 1})["query"]
        normalized = {n["from"]: n["to"] for n in query.get("normalized", [])}
        redirects = {r["from"]: r["to"] for r in query.get("redirects", [])}
        for t in batch:
            t2 = normalized.get(t, t)
            canonical[t] = redirects.get(t2, t2)

    result = sorted(set(canonical.values()))
    _save(path, result)
    return result


def get_article(title):
    """The article's {title, pageid, shortdesc, text}, with text cut at See also / References."""
    path = _cache_path("articles", title)
    if path.exists():
        return json.loads(path.read_text())

    pages, _ = _query_all({
        "titles": title,
        "redirects": 1,
        "prop": "extracts|pageprops",
        "explaintext": 1,        # plain text instead of HTML
        "ppprop": "wikibase-shortdesc",
    })
    page = next(iter(pages.values()))
    text = re.split(rf"\n=+ (?:{END_SECTIONS}) =+\n", page.get("extract", ""))[0]
    article = {
        "title": page["title"],
        "pageid": page["pageid"],
        "shortdesc": page.get("pageprops", {}).get("wikibase-shortdesc"),
        "text": text.strip(),
    }
    _save(path, article)
    return article


def get_backlinks(title):
    """Articles that link to `title`, directly or through a redirect, as a sorted list.

    The mirror image of get_links(): who links *to* the page, from all of
    Wikipedia. Links from templates such as navboxes count, as in get_links().
    """
    path = _cache_path("backlinks", title)
    if path.exists():
        return json.loads(path.read_text())

    sources, cont = set(), {}
    while True:
        data = _api_get({
            "action": "query",
            "list": "backlinks",
            "bltitle": title,
            "blnamespace": 0,        # articles only
            "bllimit": "max",        # 500 per request
            "blredirect": 1,         # also list the articles that link through a redirect
            **cont,
        })
        for b in data["query"]["backlinks"]:
            if not b.get("redirect"):          # a redirect page isn't an article...
                sources.add(b["title"])
            for r in b.get("redirlinks", []):  # ...but the articles linking to it are
                sources.add(r["title"])
        if "continue" not in data:
            break
        cont = data["continue"]
    sources.discard(title)

    result = sorted(sources)
    _save(path, result)
    return result


def get_article_count():
    """How many articles English Wikipedia has (W in Milne & Witten's in-link measure).

    Cached with the date it was fetched, since the number grows every day.
    """
    path = CACHE_DIR / "_article_count.json"
    if path.exists():
        return json.loads(path.read_text())

    stats = _api_get({"action": "query", "meta": "siteinfo", "siprop": "statistics"})["query"]["statistics"]
    result = {"articles": stats["articles"], "fetched": time.strftime("%Y-%m-%d")}
    _save(path, result)
    return result
