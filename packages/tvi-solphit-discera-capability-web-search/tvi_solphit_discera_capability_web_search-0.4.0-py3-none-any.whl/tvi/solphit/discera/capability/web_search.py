from __future__ import annotations
from typing import Dict, Any, List, AsyncGenerator

from tvi.solphit.base.logging import SolphitLogger

log = SolphitLogger.get_logger("discera.capabilities.web_search")


class WebSearchCapability:
    """
    Hello-world web_search capability.

    Contract expected by the registry/router:
      - name: unique lowercase string
      - run_once(args, **kwargs) -> dict with keys: answer, contexts (list), meta (dict)
      - run_stream(args, **kwargs) -> async generator of {'event': str, 'data': str|dict}

    `args` should at least contain:
      - question: str
      - history: List[Dict[str, str]]  # [{role, content}, ...]
    Additional kwargs can carry environment/config if you decide to use them.
    """

    name = "web_search"

    # ---------- non-streaming ----------
    def run_once(self, args: Any, **kwargs) -> Dict[str, Any]:
        q: str = (getattr(args, "question", None) or args.get("question") or "").strip()
        hints: Dict[str, Any] = kwargs.get("hints") or {}
        domain = hints.get("domain")  # e.g., "weather" if the decision hinted so

        # Hello-world answer (replace later with real search + summarization)
        answer = (
            "[web_search demo]\n"
            f"I would search the web for: “{q}”."
            + (f" (domain hint: {domain})" if domain else "")
            + "\n(This is a placeholder response; replace with real search results.)"
        )

        # Keep shape compatible with your service expectations
        return {
            "answer": answer,
            "contexts": [],  # later: snippets or URLs you gathered
            "meta": {
                "capability": self.name,
                "demo": True,
                "hints": hints,
            },
        }

    # ---------- streaming ----------
    async def run_stream(self, args: Any, **kwargs) -> AsyncGenerator[dict, None]:
        """
        Emits a minimal SSE-like stream compatible with your /api/stream UI.
        """
        q: str = (getattr(args, "question", None) or args.get("question") or "").strip()
        hints: Dict[str, Any] = kwargs.get("hints") or {}
        domain = hints.get("domain")

        # Compose demo text
        text = (
            "[web_search demo] "
            f"I would search the web for “{q}”."
            + (f" (domain hint: {domain})" if domain else "")
            + " This is placeholder text."
        )

        # Signal start
        yield {"event": "generation_started", "data": {"capability": self.name, "hints": hints}}

        # Tokenize into a few chunks to look like streaming
        for chunk in _chunk_text(text, max_len=64):
            yield {"event": "token", "data": chunk}

        # Done
        yield {"event": "generation_done", "data": {}}
        yield {"event": "done", "data": {}}


def _chunk_text(s: str, max_len: int = 64) -> List[str]:
    out: List[str] = []
    buf = s.strip()
    while buf:
        out.append(buf[:max_len])
        buf = buf[max_len:]
    return out


def register(registry):
    registry.register(WebSearchCapability())
