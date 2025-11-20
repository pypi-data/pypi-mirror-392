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
    # LOCAL FALLBACK AI (v0.4 + v0.5 merged)
    # ==========================================================
    def _local_ai(self, prompt, file_data):
        """
        Uses AST parsing to inspect Python,
        gives real syntax help + fallback personality text.
        """
        if file_data and not file_data.startswith("[CrystalAI]"):
            try:
                ast.parse(file_data)
                if "fix" in prompt.lower() or "error" in prompt.lower():
                    return "[LocalAI] File has no syntax errors. What exactly breaks?"
                return "[LocalAI] File parsed OK. Ask me to summarize or fix something."
            except SyntaxError as se:
                # Syntax help
                lineno = se.lineno or 0
                offset = se.offset or 0
                msg = f"[LocalAI] SyntaxError: {se.msg} at line {lineno}, col {offset}"
                snippet = self._snippet(file_data, lineno)
                return msg + "\n" + snippet

        # generic offline
        if "error" in prompt.lower():
            return "[LocalAI] maybe u forgot a colon or indent lol"

        return "[LocalAI] offline fallback active."

    # ==========================================================
    # ASK
    # ==========================================================
    def ask(self, text, file=None):
        file_data = self._read_file(file)
        prompt = self._build_prompt(text, file_data)

        # Real Groq request would go here
        try:
            raise Exception("simulate offline")
        except:
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
