from __future__ import annotations
import os, json, requests
from typing import Dict, Any, List, AsyncGenerator, Optional
from tvi.solphit.base.logging import SolphitLogger

# Optional LLM (ingialla)
try:
    from tvi.solphit.ingialla.ask import Generator
    _HAS_LLM = True
except Exception:
    _HAS_LLM = False

log = SolphitLogger.get_logger("discera.capabilities.code")

class CodeCapability:
    """
    Capability: code
    Purpose:
      Advanced coding help: write/refactor/fix/explain code; propose plans; emit MWEs.
    Intents:
      - "code"         : generate/modify code, explain errors
      - "code_explain" : explain code or error messages
      - "code_review"  : suggest improvements
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
            "name": CodeCapability.name,
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
            # Use 'excludes' if you ever want to soft-veto topics (the router can penalize):
            "excludes": [],
        }

    # --- Optional plugin assets (CSS/JS) ---
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
"""
        return {"css": [css], "js": []}

    # ---------- Non-streaming ----------
    def run_once(self, args: Any, **kwargs) -> Dict[str, Any]:
        q: str = (getattr(args, "question", None) or args.get("question") or "").strip()
        hints: Dict[str, Any] = kwargs.get("hints") or {}
        provider = (hints.get("provider") or "ollama")
        model    = (hints.get("model") or "codellama:13b")

        system = (
            "You are an expert software engineer. Respond with clear reasoning and ALWAYS format code using "
            "triple backticks with an explicit language label (```python, ```javascript, ```csharp, etc.). "
            "Prefer minimal, runnable examples and include brief comments. Avoid excessive prose before code."
        )
        prompt = f"{system}\n\nUSER REQUEST:\n{q}"

        # First try: Generator (may use /api/chat underneath)
        if _HAS_LLM:
            try:
                gen = Generator(provider=provider, model=model, verbose=False)
                text = gen.generate(prompt, contexts=[], history=kwargs.get("history") or []) or ""
                return {
                    "answer": text.strip(),
                    "contexts": [],
                    "meta": {"capability": self.name, "provider": provider, "model": model},
                }
            except Exception as e:
                log.error(f"[code] Generator.generate failed; falling back to /api/generate: {e}")

        # Fallback: direct Ollama /api/generate (non-stream)
        text = _ollama_generate(prompt=prompt, model=model)
        return {
            "answer": text.strip(),
            "contexts": [],
            "meta": {"capability": self.name, "provider": provider, "model": model, "fallback": "generate"},
        }

    # ---------- Streaming ----------
    async def run_stream(self, args: Any, **kwargs) -> AsyncGenerator[dict, None]:
        q: str = (getattr(args, "question", None) or args.get("question") or "").strip()
        hints: Dict[str, Any] = kwargs.get("hints") or {}
        provider = (hints.get("provider") or "ollama")
        model    = (hints.get("model") or "codellama:13b")

        system = (
            "You are an expert software engineer. Respond with clear reasoning and ALWAYS format code using "
            "triple backticks with an explicit language label. Keep explanations concise; prefer runnable examples."
        )
        prompt = f"{system}\n\nUSER REQUEST:\n{q}"

        # Announce
        yield {"event": "generation_started", "data": {"capability": self.name, "provider": provider, "model": model}}

        # Try Generator streaming first
        if _HAS_LLM:
            try:
                gen = Generator(provider=provider, model=model, verbose=False)
                if hasattr(gen, "generate_stream"):
                    for token in gen.generate_stream(prompt, contexts=[], history=kwargs.get("history") or []):  # type: ignore[attr-defined]
                        txt = str(token)
                        if txt:
                            yield {"event": "token", "data": txt}
                    yield {"event": "generation_done", "data": {}}
                    yield {"event": "done", "data": {}}
                    return
                else:
                    # No streaming available -> do a single generate and chunk locally
                    text = gen.generate(prompt, contexts=[], history=kwargs.get("history") or []) or ""
                    for chunk in _chunk_text(text, max_len=96):
                        yield {"event": "token", "data": chunk}
                    yield {"event": "generation_done", "data": {}}
                    yield {"event": "done", "data": {}}
                    return
            except Exception as e:
                log.error(f"[code] Generator streaming failed; falling back to /api/generate: {e}")

        # Fallback: call /api/generate (non-stream), then chunk locally
        try:
            text = _ollama_generate(prompt=prompt, model=model)
        except Exception as e:
            log.error(f"[code] /api/generate fallback failed: {e}")
            text = (
                "### Plan\n1. Clarify requirements\n2. Draft code\n3. Test and iterate\n\n"
                "```python\ndef hello(name: str) -> str:\n    return f\"Hello, {name}!\"\n```\n"
            )

        for chunk in _chunk_text(text, max_len=96):
            yield {"event": "token", "data": chunk}
        yield {"event": "generation_done", "data": {}}
        yield {"event": "done", "data": {}}


def _ollama_base_url() -> str:
    # Use the same env variable the service uses; your docker-compose sets OLLAMA_BASE_URL
    # to http://host.docker.internal:11434 and maps host.docker.internal for the container.  [1](https://tobivisionco-my.sharepoint.com/personal/tobias_opcenter_io/Documents/Microsoft%20Copilot%20Chat%20Files/docker-compose.yml)
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

def _ollama_generate(*, prompt: str, model: str) -> str:
    """
    Minimal direct fallback to Ollama /api/generate (non-stream).
    https://github.com/ollama/ollama/blob/main/docs/api.md (uses `prompt` and `model`).
    """
    base = _ollama_base_url().rstrip("/")
    url = f"{base}/api/generate"
    body = {"model": model, "prompt": prompt, "stream": False}
    # 60s is typically enough for a single response; adjust if your models are heavier.
    r = requests.post(url, json=body, timeout=60)
    r.raise_for_status()
    data = r.json() or {}
    text = str(data.get("response", "")).strip()
    if not text:
        # Some builds return 'message' or 'error' on failure
        msg = data.get("message") or data.get("error") or ""
        raise RuntimeError(f"Ollama /api/generate returned empty response. {msg}")
    return text

def _chunk_text(s: str, max_len: int = 96) -> List[str]:
    out: List[str] = []
    buf = (s or "").strip()
    while buf:
        out.append(buf[:max_len])
        buf = buf[max_len:]
    return out

def register(registry): registry.register(CodeCapability())