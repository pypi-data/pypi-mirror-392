# web.py
from __future__ import annotations

import re
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import httpx
import tldextract
import trafilatura

# Discera logging (matches your other capabilities)
from tvi.solphit.base.logging import SolphitLogger
log = SolphitLogger.get_logger("discera.capabilities.web")

# ---- Search backend import compatibility (ddgs preferred; fallback to duckduckgo_search) ----
DDGS_CLS = None
try:
    from ddgs import DDGS as _DDGS
    DDGS_CLS = _DDGS
except Exception:
    try:
        from duckduckgo_search import DDGS as _DDGS_OLD
        DDGS_CLS = _DDGS_OLD
    except Exception:
        DDGS_CLS = None


# ----------------- Config / Presets -----------------

SPORTS_SOURCES = {
    "espn.com", "nba.com", "mlb.com", "nhl.com", "nfl.com",
    "yahoo.com", "sports.yahoo.com", "cbssports.com", "si.com",
    "foxsports.com", "apnews.com"
}

NEWS_SOURCES = {
    "apnews.com", "reuters.com", "bbc.com", "nytimes.com", "washingtonpost.com",
    "theguardian.com", "npr.org", "bloomberg.com", "wsj.com", "cnbc.com"
}

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

STOPWORDS = {
    "a","an","the","and","or","but","if","then","else","when","while","for","to","from","in","out","on","off","of",
    "with","without","by","as","at","is","are","was","were","be","been","being","it","its","this","that","these",
    "those","i","you","he","she","we","they","them","his","her","their","our","your","yours","ours",
    "do","does","did","doing","done","can","could","should","would","may","might","must","will","shall",
    "about","after","again","against","all","also","any","both","each","few","more","most","other","some","such",
    "no","nor","not","only","own","same","so","than","too","very","just","over","into","up","down","out",
}


# ----------------- Internal Types -----------------

@dataclass
class _Hit:
    title: str
    url: str
    domain: str
    snippet: str = ""
    text: Optional[str] = None
    ok: bool = False
    err: Optional[str] = None


# ----------------- Utilities -----------------

def _normalize_ws(s: str) -> str:
    import re as _re
    return _re.sub(r"\s+", " ", s or "").strip()

def _extract_domain(url: str) -> str:
    ext = tldextract.extract(url)
    return (f"{ext.domain}.{ext.suffix}" if ext.suffix else ext.domain).lower()

def _is_article(text: str, min_chars: int = 400) -> bool:
    if not text:
        return False
    return (len(text) >= min_chars) and (text.count(".") + text.count("!") + text.count("?") >= 3)

def _sentence_split(text: str) -> List[str]:
    text = (text or "").replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\b(e\.g|i\.e|Mr|Mrs|Ms|Dr|Prof)\.", r"\1", text, flags=re.IGNORECASE)
    parts = re.split(r"(?<=[\.\?!])\s+(?=[A-Z0-9])", text)
    out = []
    for p in parts:
        s = _normalize_ws(p)
        if s:
            out.append(s)
    return out

def _tokenize(text: str) -> List[str]:
    text = (text or "").lower()
    toks = re.findall(r"[a-zA-Z0-9]+", text)
    return [t for t in toks if t not in STOPWORDS and len(t) > 1]

def _cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or not b: return 0.0
    keys = set(a) & set(b)
    num = sum(a[k]*b[k] for k in keys)
    import math as _m
    den = _m.sqrt(sum(v*v for v in a.values())) * _m.sqrt(sum(v*v for v in b.values()))
    return (num/den) if den else 0.0

def _tfidf(sent_tokens: List[List[str]]) -> Tuple[List[Dict[str,float]], Dict[str,float]]:
    from collections import Counter
    df = Counter()
    for toks in sent_tokens:
        df.update(set(toks))
    N = max(1, len(sent_tokens))
    import math as _m
    idf = {t: _m.log((N + 1) / (df_t + 1)) + 1.0 for t, df_t in df.items()}
    vecs = []
    for toks in sent_tokens:
        tf = Counter(toks)
        vecs.append({t: tf[t]*idf.get(t, 0.0) for t in tf})
    return vecs, idf

def _mmr(sentences: List[str], vecs: List[Dict[str,float]], k: int = 6, lmbda: float = 0.75) -> List[int]:
    import math as _m
    if not sentences: return []
    rel = [_m.sqrt(sum(v*v for v in vec.values())) for vec in vecs]
    chosen: List[int] = []
    cand = set(range(len(sentences)))
    while len(chosen) < min(k, len(sentences)):
        best_idx, best_score = None, -1e9
        for i in cand:
            if not chosen:
                score = rel[i]
            else:
                sim = max(_cosine(vecs[i], vecs[j]) for j in chosen)
                score = lmbda*rel[i] - (1 - lmbda)*sim
            if score > best_score:
                best_score, best_idx = score, i
        chosen.append(best_idx)  # type: ignore[arg-type]
        cand.remove(best_idx)    # type: ignore[arg-type]
    return sorted(chosen)

def _chunk_text(s: str, max_len: int = 96) -> List[str]:
    out: List[str] = []
    buf = (s or "").strip()
    while buf:
        out.append(buf[:max_len])
        buf = buf[max_len:]
    return out


# ----------------- DuckDuckGo Search & Fetch -----------------

def _build_whitelist(preset: Optional[str]) -> Optional[set]:
    if not preset: return None
    p = preset.lower()
    if p == "sports": return SPORTS_SOURCES
    if p == "news": return NEWS_SOURCES
    return None

def _boost_query_for_sports(q: str) -> str:
    extra = " score final result game schedule \"next game\""
    ql = q.lower()
    if any(k in ql for k in ["score", "result", "game", "schedule", "play"]):
        return q
    return f"{q} {extra}"

def _ddg_search(query: str, *, max_results: int, region: str, safesearch: str,
                time: Optional[str], whitelist: Optional[set]) -> List[_Hit]:
    if DDGS_CLS is None:
        raise RuntimeError("Search backend not available. Install `ddgs` (preferred) or `duckduckgo_search`.")
    hits = []
    with DDGS_CLS() as ddgs:
        try:
            raw = ddgs.text(query, region=region, safesearch=safesearch, timelimit=time, max_results=max_results*3)
        except TypeError:
            raw = ddgs.text(query, region=region, safesearch=safesearch, time=time, max_results=max_results*3)
    for h in raw:
        url = h.get("href") or h.get("url") or ""
        if not url: continue
        dom = _extract_domain(url)
        if whitelist and dom not in whitelist:
            continue
        title = h.get("title") or ""
        body = h.get("body") or ""
        hits.append(_Hit(title=_normalize_ws(title), url=url, domain=dom, snippet=_normalize_ws(body)))
        if len(hits) >= max_results:
            break
    return hits

def _fetch_and_extract(url: str, client: httpx.Client) -> Tuple[Optional[str], Optional[str]]:
    try:
        r = client.get(url, headers=DEFAULT_HEADERS, timeout=15, follow_redirects=True)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}"
        html = r.text
        txt = trafilatura.extract(html, include_comments=False, include_tables=False, url=url)
        if txt and _is_article(txt):
            return txt, None
        # fallback more permissive
        txt2 = trafilatura.extract(html, url=url)
        if txt2 and len(txt2) > 200:
            return txt2, None
        return None, "Could not extract meaningful text"
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def _summarize(hits: List[_Hit], *, summary_sentences: int = 6) -> Tuple[str, List[_Hit]]:
    cand = [h for h in hits if h.ok and h.text]
    if not cand:
        return "Sorry, I couldn’t extract readable content from the results.", []
    # prefer official/news sources a bit
    def score(h: _Hit) -> float:
        base = len(h.text or "")
        boost = 1.2 if (h.domain in SPORTS_SOURCES or h.domain in NEWS_SOURCES) else 1.0
        return base * boost
    cand.sort(key=score, reverse=True)
    used = cand[: min(6, len(cand))]

    pairs: List[Tuple[str, str]] = []
    for h in used:
        for s in _sentence_split(h.text or "")[:50]:
            if 40 <= len(s) <= 350:
                pairs.append((s, h.domain))

    if not pairs:
        return "I found sources, but couldn’t extract enough coherent sentences to summarize.", used

    sents = [s for s, _d in pairs]
    toks = [_tokenize(s) for s in sents]
    vecs, _ = _tfidf(toks)
    idx = _mmr(sents, vecs, k=summary_sentences, lmbda=0.75)
    sel = [pairs[i] for i in idx]
    summary = "\n".join("• " + s for s, _d in sel)
    return summary, used


# ----------------- ESPN JSON (exact sports) -----------------

ESPN_LEAGUE_PATHS = {
    "nba": "basketball/nba",
    "nfl": "football/nfl",
    "mlb": "baseball/mlb",
    "nhl": "hockey/nhl",
}

def _espn_schedule_url(league: str, team: str) -> str:
    base = "https://site.api.espn.com/apis/site/v2/sports"
    path = ESPN_LEAGUE_PATHS.get((league or "").lower())
    if not path:
        raise ValueError(f"Unsupported league '{league}'. Choose from: {', '.join(ESPN_LEAGUE_PATHS)}")
    return f"{base}/{path}/teams/{team.lower()}/schedule"

def _espn_fetch(league: str, team: str) -> dict:
    url = _espn_schedule_url(league, team)
    with httpx.Client(headers=DEFAULT_HEADERS, timeout=20) as client:
        r = client.get(url)
        r.raise_for_status()
        return r.json()

def _espn_last_and_next(data: dict):
    from datetime import datetime, timezone
    events = data.get("events") or []
    now = datetime.now(timezone.utc)
    last_final, next_game = None, None
    def _dt(ev):
        try:
            return datetime.fromisoformat(ev.get("date","").replace("Z","+00:00"))
        except Exception:
            return None
    for ev in events:
        status = (ev.get("status") or {}).get("type") or {}
        completed = bool(status.get("completed"))
        dt = _dt(ev)
        if completed:
            if (last_final is None) or (dt and _dt(last_final) and dt > _dt(last_final)):
                last_final = ev
        else:
            if dt and dt > now and (next_game is None or dt < _dt(next_game)):
                next_game = ev
    return last_final, next_game

def _espn_event_line(ev: dict) -> str:
    if not ev: return "No event data."
    comps = (ev.get("competitions") or [{}])[0].get("competitors") or []
    home = next((c for c in comps if c.get("homeAway") == "home"), None)
    away = next((c for c in comps if c.get("homeAway") == "away"), None)
    def lab(c):
        t = c.get("team") or {}
        return t.get("abbreviation") or t.get("shortDisplayName") or t.get("displayName") or "?"
    status = (ev.get("status") or {}).get("type") or {}
    completed = bool(status.get("completed"))
    detail = status.get("shortDetail") or status.get("description") or ""
    vs = f"{lab(away)} at {lab(home)}"
    if completed:
        hs = home.get("score"); as_ = away.get("score")
        if hs is not None and as_ is not None:
            return f"{vs} — Final {as_}-{hs} ({detail})"
        return f"{vs} — Final ({detail})"
    else:
        # show ISO time; letting caller or frontend localize if needed
        return f"{vs} — {ev.get('date','').replace('T',' ').replace('Z',' UTC')} ({detail or 'Scheduled'})"


# ----------------- Capability -----------------

class WebSearchCapability:
    """
    Capability: web
    Purpose:
      Answers questions by searching the web and summarizing sources OR, for sports,
      reading ESPN JSON for exact scores/schedules.
    Intents:
      - "web_answer": free web search + summary
      - "sports_result": last game result for a team (ESPN)
      - "sports_next_game": next scheduled game for a team (ESPN)
    """
    name = "web_search"

    @staticmethod
    def descriptor() -> Dict[str, Any]:
        return {
            "name": WebSearchCapability.name,
            "description": (
                "Searches the web and summarizes results with citations; "
                "can also use ESPN JSON for exact scores/schedules (NBA/NFL/MLB/NHL)."
            ),
            "intents": ["web_answer", "sports_result", "sports_next_game"],
            "examples": [
                "What was the result of the Detroit Pistons game last night?",
                "When do the Cardinals play their next game?",
                "Summarize today's news about Nvidia earnings.",
            ],
            "tags": ["web", "search", "summary", "sports", "scores", "schedule", "news"],
            "excludes": [],
        }

    # ---------- Public API ----------

    def run_once(self, args: Any, **kwargs) -> Dict[str, Any]:
        """
        Inputs:
          args.question: user query (string)
          kwargs.hints (optional dict) may include:
            mode: "ddg" | "espn" (default "ddg")
            preset: "sports" | "news" | None   [ddg]
            time: "d"|"w"|"m"|"y"|None         [ddg]
            max: int (default 8)               [ddg]
            summary_sentences: int (default 6) [ddg]
            region: str (default "wt-wt")      [ddg]
            safesearch: str (default "moderate")[ddg]
            league: "nba"|"nfl"|"mlb"|"nhl"    [espn]
            team: team abbreviation, e.g., DET, STL, ARI  [espn]
        """
        q: str = (getattr(args, "question", None) or args.get("question") or "").strip()
        hints: Dict[str, Any] = kwargs.get("hints") or {}
        mode = (hints.get("mode") or "ddg").lower()

        if mode == "espn":
            league = (hints.get("league") or "").lower()
            team = (hints.get("team") or "").upper()
            if not league or not team:
                return {
                    "answer": "ESPN mode requires 'league' and 'team' hints (e.g., league=nba, team=DET).",
                    "contexts": [],
                    "meta": {"capability": self.name, "mode": "espn", "error": "missing_league_or_team"},
                }
            try:
                data = _espn_fetch(league, team)
                last_final, next_game = _espn_last_and_next(data)
                want_last = any(k in q.lower() for k in ["last night", "last game", "result", "score", "final"])
                want_next = any(k in q.lower() for k in ["next", "when do", "upcoming", "schedule"])

                lines: List[str] = []
                if want_last and last_final:
                    lines += ["Last game:", "  " + _espn_event_line(last_final)]
                if want_next and next_game:
                    lines += ["Next game:", "  " + _espn_event_line(next_game)]
                if not lines:
                    if last_final:
                        lines += ["Last game:", "  " + _espn_event_line(last_final)]
                    if next_game:
                        lines += ["Next game:", "  " + _espn_event_line(next_game)]
                if not lines:
                    lines = ["No game data found."]

                url = _espn_schedule_url(league, team)
                answer = "\n".join(lines)
                return {
                    "answer": answer,
                    "contexts": [url],
                    "meta": {"capability": self.name, "mode": "espn", "league": league, "team": team},
                }
            except Exception as e:
                log.error(f"[web] ESPN fetch failed: {e}")
                return {
                    "answer": f"ESPN fetch failed: {e}",
                    "contexts": [],
                    "meta": {"capability": self.name, "mode": "espn", "error": str(e)},
                }

        # --- DuckDuckGo summarize path ---
        preset = hints.get("preset")
        time = hints.get("time")  # d|w|m|y
        region = hints.get("region") or "wt-wt"
        safesearch = hints.get("safesearch") or "moderate"
        max_results = int(hints.get("max") or 8)
        summary_sentences = int(hints.get("summary_sentences") or 6)

        wl = _build_whitelist(preset)
        boosted = _boost_query_for_sports(q) if preset == "sports" else q

        def _try(bq: str, whitelist: Optional[set], tim: Optional[str]) -> List[_Hit]:
            try:
                return _ddg_search(
                    bq, max_results=max_results, region=region,
                    safesearch=safesearch, time=tim, whitelist=whitelist
                )
            except Exception as se:
                log.error(f"[web] search error: {se}")
                return []

        hits = _try(boosted, wl, time)
        if not hits and wl:
            log.info("[web] 0 results with whitelist; retrying without source filter...")
            hits = _try(boosted, None, time)
        if not hits and time:
            log.info("[web] still 0; retrying without time filter...")
            hits = _try(boosted, None if wl else wl, None)

        if not hits:
            return {
                "answer": "No search results found. Try broadening the query. For sports, set hints.mode='espn'.",
                "contexts": [],
                "meta": {"capability": self.name, "mode": "ddg", "query": q, "boosted": boosted},
            }

        # fetch & extract synchronously (keeps integration simple)
        with httpx.Client(headers=DEFAULT_HEADERS) as client:
            for h in hits:
                txt, err = _fetch_and_extract(h.url, client)
                h.text, h.err = txt, err
                h.ok = txt is not None

        summary, used = _summarize(hits, summary_sentences=summary_sentences)

        # Build a source list for contexts
        contexts = [u.url for u in used]
        # Present sources inline after summary
        if used:
            src_lines = ["", "Sources:"] + [f"- [{u.domain}] {u.title or u.url}\n  {u.url}" for u in used]
            answer = summary + "\n" + "\n".join(src_lines)
        else:
            answer = summary

        return {
            "answer": answer,
            "contexts": contexts,
            "meta": {
                "capability": self.name,
                "mode": "ddg",
                "preset": preset,
                "time": time,
                "query": q,
                "boosted": boosted,
                "summary_sentences": summary_sentences,
            },
        }

    async def run_stream(self, args: Any, **kwargs):
        """
        Streams the final answer as tokens. Matches your event framing:
          - generation_started
          - token (chunked)
          - generation_done
          - done
        """
        result = self.run_once(args, **kwargs)
        text = result.get("answer") or ""
        yield {"event": "generation_started", "data": {"capability": self.name}}
        for chunk in _chunk_text(text, max_len=96):
            yield {"event": "token", "data": chunk}
        yield {"event": "generation_done", "data": {}}
        yield {"event": "done", "data": {}}


def register(registry):
    registry.register(WebSearchCapability())