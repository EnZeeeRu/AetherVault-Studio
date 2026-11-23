"""Memory normalization, deduplication/compaction, and 1-hop keyword mind-map helpers."""
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher

EXCLUSIVE_MEMORY_CATEGORIES = {"user_name", "user_identity", "user_location", "location", "user_zip", "zip_code"}
DEFAULT_STOPWORDS = {
    "the", "and", "for", "that", "this", "with", "you", "your", "are", "was",
    "have", "has", "had", "not", "but", "what", "when", "where", "who", "why",
    "from", "they", "them", "their", "there", "about", "into", "just", "like",
}


def normalize_fact(text: str) -> str:
    s = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
    return re.sub(r"\s+", " ", s).strip()


def extract_terms(text: str, stopwords: set[str] = DEFAULT_STOPWORDS) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9_\x27-]{4,}", (text or "").lower())
    return [w for w in words if w not in stopwords and not w.isdigit()]


class KeywordMindMap:
    """Bounded 1-hop keyword co-occurrence graph for context & lore grounding."""

    def __init__(self, max_nodes: int = 250, max_neighbors: int = 5):
        self.max_nodes = max(20, int(max_nodes))
        self.max_neighbors = max(1, int(max_neighbors))
        self.edges: dict[str, list[tuple[str, int]]] = {}

    def rebuild_from_items(self, items: list[tuple[str, int]]) -> int:
        co: dict[str, Counter] = defaultdict(Counter)
        for text, weight in items[:500]:
            w_val = max(1, int(weight or 1))
            kws = list(dict.fromkeys(extract_terms(text)))
            for w in kws:
                for peer in kws:
                    if peer != w:
                        co[w][peer] += w_val
        ranked = sorted(co.items(), key=lambda kv: sum(kv[1].values()), reverse=True)[:self.max_nodes]
        self.edges = {w: cnt.most_common(self.max_neighbors) for w, cnt in ranked}
        return len(self.edges)

    def expand(self, query_text: str, max_hops: int = 4) -> list[str]:
        base = extract_terms(query_text)
        expanded = list(dict.fromkeys(base))
        cap = len(base) + max(1, int(max_hops))
        for kw in base[:4]:
            for nb, _ in self.edges.get(kw, [])[:2]:
                if nb not in expanded:
                    expanded.append(nb)
                if len(expanded) >= cap:
                    return expanded
        return expanded


def deduplicate_memory_rows(rows: list[dict], fuzzy_threshold: float = 0.86) -> dict:
    """Pure deterministic memory deduplicator over already-loaded memory dicts."""
    seen_excl: set[str] = set()
    kept: list[dict] = []
    inactive_ids: list[int] = []
    merged_count = 0
    superseded_count = 0

    for r in rows:
        rid = int(r["id"])
        cat = (r.get("category") or "active_state").strip()
        cat_low = cat.lower()
        fact = (r.get("fact") or "").strip()
        hits = int(r.get("hits") or 1)
        norm = normalize_fact(fact)

        if not norm:
            inactive_ids.append(rid)
            superseded_count += 1
            continue

        if cat_low in EXCLUSIVE_MEMORY_CATEGORIES:
            if cat_low in seen_excl:
                inactive_ids.append(rid)
                superseded_count += 1
                continue
            seen_excl.add(cat_low)

        dup = None
        for k in kept:
            if k["norm"] == norm:
                dup = k
                break
            if k["cat_low"] == cat_low and abs(len(k["norm"]) - len(norm)) < 45:
                if SequenceMatcher(None, k["norm"], norm).ratio() >= fuzzy_threshold:
                    dup = k
                    break

        if dup is not None:
            best_fact = fact if len(fact) > len(dup["fact"]) else dup["fact"]
            dup["fact"] = best_fact
            dup["norm"] = normalize_fact(best_fact)
            dup["hits"] = int(dup["hits"]) + hits
            inactive_ids.append(rid)
            merged_count += 1
        else:
            kept.append({"id": rid, "category": cat, "cat_low": cat_low, "fact": fact, "norm": norm, "hits": hits})

    return {
        "kept": kept,
        "inactive_ids": inactive_ids,
        "merged": merged_count,
        "superseded": superseded_count,
    }
