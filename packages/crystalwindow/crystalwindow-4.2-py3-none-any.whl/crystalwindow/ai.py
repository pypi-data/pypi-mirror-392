# ==========================================================
# CrystalAI v0.6 — Unified Engine
# ----------------------------------------------------------
# Combines:
#   - v0.4: auto-fix, AST parser, docs index, diff tools
#   - v0.5: personality, library ingestion, safe key check
#   - Groq fallback, local fallback, file analysis
# ==========================================================

import os
import ast
import difflib
from typing import Optional, Dict, Any
import requests
import groq


# ==========================================================
# Response Wrapper
# ==========================================================
class CrystalAIResponse:
    def __init__(self, text: str, meta: Optional[Dict[str, Any]] = None):
        self.text = text
        self.meta = meta or {}

    def __str__(self):
        return self.text


# ==========================================================
# MAIN ENGINE
# ==========================================================
class AI:
    DEFAULT_MODEL = "llama-3.1-8b"
    DEFAULT_PERSONALITY = (
        "You are CrystalWindow AI. You help users with Python code, "
        "debugging, errors, docs, and file analysis. "
        "Be friendly, technical, clear, and precise."
    )
    PLACEHOLDER_KEY = "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"

    # ------------------------------------------------------
    def __init__(self, key=None, model=None):
        # --- KEY VALIDATION ---
        if not key or len(key) < 20 or " " in key:
            print("[CrystalAI] Warning: Invalid or missing key → using placeholder. To get a Fixed Key go to 'console.groq.com/keys'")
            self.key = self.PLACEHOLDER_KEY
        else:
            self.key = key

        # --- MODEL VALIDATION ---
        if not model or not isinstance(model, str) or len(model) < 3:
            print("[CrystalAI] Unknown model → using default.")
            self.model = self.DEFAULT_MODEL
        else:
            self.model = model

        # Persona
        self.personality = self.DEFAULT_PERSONALITY

        # Library knowledge (loaded .py files)
        self.library_context = ""

        # v0.4 memory system (optional)
        self.memory = []
        self.use_memory = True

        # v0.4 toggle for forcing local engine
        self.force_local = False

    # ==========================================================
    # PERSONALITY
    # ==========================================================
    def set_personality(self, txt):
        if not isinstance(txt, str) or len(txt.strip()) < 10:
            print("Oops! thats not how to use it—reverting to default.")
            self.personality = self.DEFAULT_PERSONALITY
            return

        if len(txt) > 3000:
            print("Oops, personality too long → using default.")
            self.personality = self.DEFAULT_PERSONALITY
            return

        self.personality = txt.strip()

    # ==========================================================
    # LIBRARY INGESTION
    # ==========================================================
    def index_library(self, folder):
        """
        Load all Python files as context for smarter answers.
        """
        out = []
        if not os.path.exists(folder):
            print("[CrystalAI] Library folder not found.")
            return

        for root, _, files in os.walk(folder):
            for f in files:
                if f.endswith(".py"):
                    try:
                        path = os.path.join(root, f)
                        with open(path, "r", encoding="utf8") as fp:
                            out.append(f"# FILE: {path}\n" + fp.read() + "\n\n")
                    except:
                        pass

        self.library_context = "\n".join(out)

    # ==========================================================
    # FILE READER
    # ==========================================================
    def _read_file(self, path):
        if not path:
            return None
        if not os.path.exists(path):
            return f"[CrystalAI] file not found: {path}"
        try:
            with open(path, "r", encoding="utf8") as f:
                return f.read()
        except:
            return "[CrystalAI] couldnt read file."

    # ==========================================================
    # PROMPT BUILDER (Unified)
    # ==========================================================
    def _build_prompt(self, user_text, file_data=None):
        final = (
            f"[SYSTEM]\n{self.personality}\n\n"
            f"[USER]\n{user_text}\n\n"
        )

        if self.use_memory and self.memory:
            final += "[MEMORY]\n"
            for m in self.memory[-6:]:
                final += f"User: {m['user']}\nAI: {m['ai']}\n"
            final += "\n"

        if self.library_context:
            final += f"[LIBRARY]\n{self.library_context}\n\n"

        if file_data:
            final += f"[FILE]\n{file_data}\n\n"

        return final

    def _save_memory(self, user, ai):
        self.memory.append({"user": user, "ai": ai})
        if len(self.memory) > 60:
            self.memory.pop(0)

    # ==========================================================
    # LOCAL FALLBACK AI (modern, useful, not dumb)
    # ==========================================================
    def _local_ai(self, prompt, file_data):
        """
        Improved fallback mode:
        - If file provided → real AST analysis
        - If general question → helpful offline response
        - No more random jokes or irrelevant "forgot a colon"
        """

        # --- If file provided, try real Python AST parsing ---
        if file_data and not file_data.startswith("[CrystalAI]"):
            try:
                ast.parse(file_data)
                return (
                    "[LocalAI] I was able to parse the file successfully.\n"
                    "There are no syntax errors.\n"
                    "Ask me to explain, summarize, refactor, or improve something."
                )
            except SyntaxError as se:
                lineno = se.lineno or 0
                offset = se.offset or 0
                msg = (
                    f"[LocalAI] SyntaxError detected:\n"
                    f"• Message: {se.msg}\n"
                    f"• Line: {lineno}\n"
                    f"• Column: {offset}\n\n"
                )
                snippet = self._snippet(file_data, lineno)
                return msg + snippet

        # --- General offline fallback (safe + useful) ---
        lower = prompt.lower()

        # Code-related queries
        if "fix" in lower or "error" in lower or "bug" in lower:
            return (
                "[LocalAI] I can't reach Groq right now,\n"
                "but here's what I can do offline:\n"
                "• Check for syntax problems if you provide a file\n"
                "• Suggest common Python mistakes\n\n"
                "Tip: try again once Groq is reachable for full debugging."
            )

        # Regular questions (time, math, writing, etc.)
        if any(x in lower for x in ["time", "story", "game", "explain", "python"]):
            return (
                "[LocalAI] I'm offline, but I can still give general help:\n"
                "- Ask me Python questions\n"
                "- Ask for concepts, writing tips, structure examples\n"
                "- Provide a file and I can analyze it with AST\n"
            )

        # Catch-all fallback
        return (
            "[LocalAI] Offline mode enabled.\n"
            "I can still analyze Python code and help with general knowledge.\n"
            "Once online, Groq will give full intelligent responses."
        )

    # ==========================================================
    # ASK (Groq → fallback)
    # ==========================================================
    def ask(self, text, file=None):
        file_data = self._read_file(file)
        prompt = self._build_prompt(text, file_data)

        # Try to call Groq normally
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": self.personality},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3
            }

            import requests
            r = requests.post(url, json=payload, headers=headers, timeout=8)
            data = r.json()

            if "error" in data:
                raise RuntimeError(data["error"])

            resp = data["choices"][0]["message"]["content"]

        except Exception:
            # Groq unreachable → fallback
            resp = self._local_ai(prompt, file_data)

        self._save_memory(text, resp)
        return CrystalAIResponse(resp)

    # ==========================================================
    # ASK (terminal)
    # ==========================================================
    def ask_t(self, text, file=None):
        return self.ask(f"[TERMINAL] {text}", file)

    # ==========================================================
    # AUTO FIX CODE (v0.4)
    # ==========================================================
    def fix_code(self, file_path):
        orig = self._read_file(file_path)

        if not orig or orig.startswith("[CrystalAI]"):
            return CrystalAIResponse(orig or "[CrystalAI] file missing")

        try:
            ast.parse(orig)
            return CrystalAIResponse("[AI] No syntax errors found.")
        except SyntaxError as se:
            fixed, notes = self._simple_fix(orig, se)
            diff = self._make_diff(orig, fixed)
            pretty = "[AI] Auto-fix result:\n" + "\n".join(notes) + "\n\n" + diff
            return CrystalAIResponse(pretty, {"diff": diff, "notes": notes})

    # ==========================================================
    # SIMPLE AUTO-FIX ENGINE
    # ==========================================================
    def _simple_fix(self, src, syntax_error):
        notes = []
        lines = src.splitlines()
        msg = getattr(syntax_error, "msg", "")
        lineno = syntax_error.lineno or 0

        # missing colon
        if "expected" in msg and ":" in msg:
            if 1 <= lineno <= len(lines):
                line = lines[lineno - 1].rstrip()
                if not line.endswith(":"):
                    lines[lineno - 1] = line + ":"
                    notes.append("[fix] added missing ':'")
                    candidate = "\n".join(lines)
                    try:
                        ast.parse(candidate)
                        return candidate, notes
                    except:
                        pass

        # fallback
        notes.append("[info] auto-fix could not fix everything")
        return src, notes

    # ==========================================================
    # DIFF UTIL
    # ==========================================================
    def _make_diff(self, old, new):
        return "\n".join(
            difflib.unified_diff(
                old.splitlines(),
                new.splitlines(),
                fromfile="old",
                tofile="new",
                lineterm=""
            )
        )

    # ==========================================================
    # SNIPPET HELPER
    # ==========================================================
    def _snippet(self, src, lineno, ctx=2):
        lines = src.splitlines()
        start = max(0, lineno - ctx - 1)
        end = min(len(lines), lineno + ctx)
        out = []
        for i in range(start, end):
            mark = "->" if (i + 1) == lineno else "  "
            out.append(f"{mark} {i+1:4}: {lines[i]}")
        return "\n".join(out)

# ==========================================================
# END OF ENGINE
# ==========================================================
