# ==========================================================
# CrystalAI v0.7 — Self-Contained Symbolic Engine
# ----------------------------------------------------------
# Focus: Pure Python 'thinking' (Knowledge Graph/Rule-Based)
# Changes:
#   - Refactored _local_ai to _symbolic_engine
#   - Added a simple knowledge base (K-Graph)
#   - Added context/intent matching for 'thinking'
#   - Removed Groq/External API integration
# ==========================================================

import os
import ast
import difflib
from typing import Optional, Dict, Any, List
# Removed requests and groq imports as they are no longer needed
# Removed import groq (if it was present)

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
    DEFAULT_MODEL = "PURE_SYMBOLIC"
    DEFAULT_PERSONALITY = (
        "You are CrystalMind AI, a completely self-coded, symbolic engine. "
        "I process information using an internal rule-base and knowledge graph. "
        "I can reason about simple code and defined concepts."
    )
    # Key is ignored in this self-contained mode, but kept for signature consistency
    PLACEHOLDER_KEY = "PURE_SYMBOLIC_KEY_IGNORED" 

    # ------------------------------------------------------
    def __init__(self, key=None, model=None):
        # --- KEY/MODEL SETUP (for consistency, though ignored) ---
        self.key = self.PLACEHOLDER_KEY
        self.model = self.DEFAULT_MODEL
        self.personality = self.DEFAULT_PERSONALITY

        # --- PURE AI KNOWLEDGE BASE (The 'Thinking' Core) ---
        self.knowledge_graph: Dict[str, Any] = self._build_knowledge_graph()

        # v0.4 memory system (optional)
        self.memory: List[Dict[str, str]] = []
        self.use_memory = True

        # v0.4 toggle for forcing local engine
        self.force_local = True # Always True for a self-contained AI

        # Library knowledge (loaded .py files)
        self.library_context = ""

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
        (Context is used in prompt but processed by local engine's rules)
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
    # PURE AI KNOWLEDGE BASE (Self-Contained 'Knowledge')
    # ==========================================================
    def _build_knowledge_graph(self) -> Dict[str, Any]:
        """
        Defines the internal knowledge the pure AI can reason with.
        """
        return {
            "python": {
                "desc": "A high-level, interpreted programming language.",
                "keywords": ["language", "interpreted", "high-level"],
                "syntax": {
                    "if_statement": "if condition: ... else: ...",
                    "loop": "for item in iterable: ..."
                }
            },
            "ast": {
                "desc": "Abstract Syntax Tree. Used for parsing code structure.",
                "keywords": ["parsing", "code", "structure", "tree"]
            },
            "fix_code": {
                "rule": "look for SyntaxError, especially missing colons or mismatched brackets",
                "keywords": ["fix", "error", "bug", "syntax"]
            }
        }

    # ==========================================================
    # PURE AI 'THINKING' ENGINE (Replaces _local_ai)
    # ==========================================================
    def _symbolic_engine(self, prompt: str, file_data: Optional[str]) -> str:
        """
        Simulates 'thinking' using only internal rules and the knowledge graph.
        """
        output = ["[SymbolicEngine] Processing request..."]
        lower_prompt = prompt.lower()

        # --- Stage 1: File Analysis (Real Python AST) ---
        if file_data and not file_data.startswith("[CrystalAI]"):
            output.append("\n[Stage 1: Code Parsing]")
            try:
                ast.parse(file_data)
                output.append("✅ **No Syntax Errors Detected** (via AST).")
                output.append("The code is structurally sound. Ask for refactoring or explanation.")
                return "\n".join(output)
            except SyntaxError as se:
                # Use the built-in fix rule from the knowledge graph
                fix_rule = self.knowledge_graph["fix_code"]["rule"]
                lineno = se.lineno or 0
                offset = se.offset or 0
                msg = (
                    f"❌ **SyntaxError Detected** (via AST):\n"
                    f"• Message: {se.msg}\n"
                    f"• Line: {lineno}\n"
                    f"• Column: {offset}\n"
                    f"• Rule suggestion: {fix_rule}"
                )
                output.append(msg)
                output.append(self._snippet(file_data, lineno))
                return "\n".join(output)

        # --- Stage 2: Knowledge Graph Lookup (Rule-Based Reasoning) ---
        output.append("\n[Stage 2: Symbolic Lookup]")

        # Check for concepts the AI 'knows'
        found_concept = False
        for key, knowledge in self.knowledge_graph.items():
            if key in lower_prompt or any(k in lower_prompt for k in knowledge.get("keywords", [])):
                if key == "fix_code": continue # Already handled in Stage 1

                output.append(f"🧠 Found Concept: **{key.upper()}**")
                output.append(f"Description: {knowledge.get('desc', 'No detailed description.')}")
                
                # Simple reasoning about related syntax
                if 'syntax' in knowledge:
                    output.append("Related Syntax:")
                    for syn, code in knowledge['syntax'].items():
                        output.append(f"  - {syn.replace('_', ' ')}: `{code}`")
                
                found_concept = True
                break
        
        if not found_concept:
            output.append("❓ Concept Unknown: I am limited to my internal knowledge base (Python, AST, Fix Code).")
            output.append("Please ask about a defined concept or provide a file for AST analysis.")


        return "\n".join(output)

    # ==========================================================
    # ASK (Pure Symbolic Engine)
    # ==========================================================
    def ask(self, text, file=None):
        file_data = self._read_file(file)
        prompt = self._build_prompt(text, file_data)
        
        # We skip the external API call entirely, relying on the symbolic engine
        resp = self._symbolic_engine(prompt, file_data)

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
            # Adjusted line formatting for clarity
            out.append(f"{mark} {i+1:<4}: {lines[i]}")
        return "\n".join(out)

# ==========================================================
# END OF PURE SYMBOLIC ENGINE
# ==========================================================