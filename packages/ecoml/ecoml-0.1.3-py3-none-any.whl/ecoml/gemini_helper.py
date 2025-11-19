import os
from pathlib import Path
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except:
    genai = None


class GeminiAdvisor:

    def __init__(self):
        root = Path(__file__).resolve().parents[1]
        load_dotenv(root / ".env")

        key = os.getenv("GEMINI_API_KEY")
        if not key:
            print("⚠ Gemini disabled – no API key found")
            self.enabled = False
            return

        if not genai:
            print("⚠ Gemini client missing (pip install google-generativeai)")
            self.enabled = False
            return

        genai.configure(api_key=key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.enabled = True
        print("🤖 Gemini Enabled ✓")

    # ------------------------------------------------------
    def ask(self, prompt: str) -> str | None:
        """One-line optimization advice"""
        try:
            out = self.model.generate_content(prompt).text.strip()
            return out
        except:
            return None

    # ------------------------------------------------------
    def generate_fix(self, err: Exception, code: str | None):
        """Generate 1-line fix suggestion"""
        prompt = f"""
You are a senior Python debugger.

Error:
{err}

Code that triggered it:
{code}

Give **ONE LINE FIX ONLY**.
"""
        return self.ask(prompt)
