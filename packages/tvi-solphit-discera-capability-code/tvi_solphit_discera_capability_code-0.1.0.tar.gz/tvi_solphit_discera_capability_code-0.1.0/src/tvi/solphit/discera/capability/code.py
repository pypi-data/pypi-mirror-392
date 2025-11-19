from __future__ import annotations
from typing import Dict, Any, List, AsyncGenerator, Optional
from tvi.solphit.base.logging import SolphitLogger

# Optional LLM (ingialla)
try:
    from tvi.solphit.ingialla.ask import Generator
    _HAS_LLM = True
except Exception:
    _HAS_LLM = False

log = SolphitLogger.get_logger("discera.capabilities.code")

class CodeTaskCapability:
    """
    Capability: code
    Purpose:
      Advanced coding help: write/refactor/fix/explain code; propose plans; emit MWEs.
    Intents:
      - "code"     : generate/modify code, explain errors
      - "code_explain"  : explain code or error messages
      - "code_review"   : suggest improvements
    Inputs:
      - question (str)
      - history (list[dict])   # optional
      - hints (dict)           # may include provider/model overrides
    Outputs:
      - answer (markdown with fenced code blocks)
      - contexts (optional links)
      - meta { capability, provider, model }
    """
    name = "code"

    @staticmethod
    def descriptor() -> Dict[str, Any]:
        return {
            "name": CodeTaskCapability.name,
            "description": (
                "Handles programming requests: generate, refactor, fix, and explain code; "
                "provides examples, reviews, and step-wise plans. Returns fenced code blocks with language labels."
            ),
            "intents": ["code", "code_explain", "code_review"],
            "examples": [
                "Write a Python function that merges two dicts with conflict resolution.",
                "Explain and fix 'TypeError: cannot read properties of undefined' in JavaScript.",
                "Refactor a C# service class to follow SOLID and add unit tests."
            ],
            "tags": ["coding", "development", "programming", "errors", "refactor", "fix", "code"],
        }

    # --- Optional plugin assets (CSS/JS) to be injected by the Web UI ---
    # Keep it minimal and self-contained. Avoid globals and heavy JS by default.
    @staticmethod
    def assets() -> Dict[str, List[str]]:
        css = r"""
/* Discera · code capability styling */
.discera pre code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono",
               "Courier New", monospace;
  font-size: 0.95rem;
}
.discera pre {
  background: #0b0b0b;
  color: #e5e7eb;
  border: 1px solid #1f2937;
  border-radius: 8px;
  padding: 12px 14px;
  overflow: auto;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}
.discera code:not(pre code) {
  background: #111827;
  color: #e5e7eb;
  padding: 2px 6px;
  border-radius: 6px;
  border: 1px solid #1f2937;
}
/* Optional language label override if present via CSS content (non-critical) */
"""
        # No JS needed for now; your app.js already renders fenced code nicely.
        # (If you later want JS—for copy buttons, line numbers, etc.—return it here.)
        return {"css": [css], "js": []}

    # ---------- Non-streaming ----------
    def run_once(self, args: Any, **kwargs) -> Dict[str, Any]:
        q: str = (getattr(args, "question", None) or args.get("question") or "").strip()
        hints: Dict[str, Any] = kwargs.get("hints") or {}
        provider = (hints.get("provider") or "ollama")
        model    = (hints.get("model") or "codellama:13b")

        if not _HAS_LLM:
            # Minimal fallback that still returns code fences
            answer = (
                "I don't have a code model available right now, but here's a structured stub you can adapt:\n\n"
                "### Plan\n"
                "1. Clarify inputs and outputs\n"
                "2. Draft a minimal function\n"
                "3. Add tests and iterate\n\n"
                "#### Example (Python)\n"
                "```python\n"
                "def hello(name: str) -> str:\n"
                "    return f\"Hello, {name}!\"\n"
                "```\n"
            )
            return {"answer": answer, "contexts": [], "meta": {"capability": self.name, "provider": None, "model": None}}

        # System guidance to produce clean, fenced, copy-paste-ready code
        system = (
            "You are an expert software engineer. Respond with clear reasoning and ALWAYS format code using "
            "triple backticks with an explicit language label (```python, ```javascript, ```csharp, etc.). "
            "Prefer minimal, runnable examples and include brief comments. Avoid excessive prose before code."
        )
        gen = Generator(provider=provider, model=model, verbose=False)
        prompt = f"{system}\n\nUSER REQUEST:\n{q}"
        answer = gen.generate(prompt, contexts=[], history=kwargs.get("history") or []) or ""

        return {
            "answer": (answer or "").strip(),
            "contexts": [],
            "meta": {"capability": self.name, "provider": provider, "model": model},
        }

    # ---------- Streaming ----------
    async def run_stream(self, args: Any, **kwargs) -> AsyncGenerator[dict, None]:
        q: str = (getattr(args, "question", None) or args.get("question") or "").strip()
        hints: Dict[str, Any] = kwargs.get("hints") or {}
        provider = (hints.get("provider") or "ollama")
        model    = (hints.get("model") or "codellama:13b")

        # Announce generation
        yield {"event": "generation_started", "data": {"capability": self.name, "provider": provider, "model": model}}

        if not _HAS_LLM:
            # Fallback streaming of a small static snippet
            stub = (
                "### Plan\n1. Clarify requirements\n2. Draft code\n3. Test and iterate\n\n"
                "```python\ndef hello(name: str) -> str:\n    return f\"Hello, {name}!\"\n```\n"
            )
            for chunk in _chunk_text(stub, max_len=96):
                yield {"event": "token", "data": chunk}
            yield {"event": "generation_done", "data": {}}
            yield {"event": "done", "data": {}}
            return

        system = (
            "You are an expert software engineer. Respond with clear reasoning and ALWAYS format code using "
            "triple backticks with an explicit language label. Keep explanations concise; prefer runnable examples."
        )
        gen = Generator(provider=provider, model=model, verbose=False)
        prompt = f"{system}\n\nUSER REQUEST:\n{q}"

        # Stream chunks if available, else fall back to non-streaming
        if hasattr(gen, "generate_stream"):
            for token in gen.generate_stream(prompt, contexts=[], history=kwargs.get("history") or []):  # type: ignore[attr-defined]
                txt = str(token)
                if txt:
                    yield {"event": "token", "data": txt}
        else:
            full = gen.generate(prompt, contexts=[], history=kwargs.get("history") or []) or ""
            for chunk in _chunk_text(full, max_len=96):
                yield {"event": "token", "data": chunk}

        yield {"event": "generation_done", "data": {}}
        yield {"event": "done", "data": {}}

def _chunk_text(s: str, max_len: int = 96) -> List[str]:
    out: List[str] = []
    buf = s.strip()
    while buf:
        out.append(buf[:max_len])
        buf = buf[max_len:]
    return out

def register(registry): registry.register(CodeTaskCapability())