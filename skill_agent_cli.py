"""
Skill-Verse Autonomous AI Agent (100% Keyless with Local Ollama)
Zero API Keys Required • Runs completely locally on your PC
"""
import sys
import json
import urllib.request
import urllib.parse
import re

# ─── AGENT KNOWLEDGE & DATABASE ───────────────────────────────────────────────
MOCK_DB_SKILLS = [
    {"user": "Priya S.", "teaches": "Python & Django", "wants": "Acoustic Guitar", "rating": 4.9, "level": "Expert"},
    {"user": "Arjun M.", "teaches": "Acoustic Guitar", "wants": "Python & Django", "rating": 5.0, "level": "Advanced"},
    {"user": "Elena R.", "teaches": "Spanish Language", "wants": "UI/UX Design", "rating": 4.9, "level": "Native"},
    {"user": "David L.", "teaches": "UI/UX & Figma", "wants": "Spanish Language", "rating": 4.8, "level": "Professional"},
    {"user": "Marcus V.", "teaches": "Sourdough Baking", "wants": "Digital Marketing", "rating": 4.7, "level": "Chef"},
    {"user": "Sara C.", "teaches": "Digital Marketing", "wants": "Sourdough Baking", "rating": 4.9, "level": "Specialist"},
]

def query_ollama(prompt, model="llama3.2:1b"):
    """Query local Ollama instance on http://localhost:11434"""
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 300}
    }
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=25) as response:
            res = json.loads(response.read().decode('utf-8'))
            return res.get('response', '').strip()
    except Exception:
        return None


# ─── AGENT CONTROLLER ─────────────────────────────────────────────────────────
class SkillVerseAgent:
    def __init__(self):
        self.name = "Skye"

    def match_tool(self, query):
        q = query.lower()
        return [s for s in MOCK_DB_SKILLS if q in s["teaches"].lower() or q in s["wants"].lower()]

    def ask(self, user_msg):
        # 1. Matchmaker Tool Intent
        if any(w in user_msg.lower() for w in ["find", "match", "partner", "who teaches", "swap with"]):
            cleaned = re.sub(r'\b(find|me|a|partner|who|teaches|for|to|swap|with|matches)\b', '', user_msg.lower()).strip()
            matches = self.match_tool(cleaned)
            if matches:
                res = f"🤖 **{self.name} Agent found {len(matches)} matching swap partners:**\n\n"
                for m in matches:
                    res += f"• **{m['user']}** (★ {m['rating']}) — Teaches: `{m['teaches']}` | Wants: `{m['wants']}`\n"
                return res

        # 2. Local Ollama LLM Generation
        ollama_prompt = (
            f"You are Skye, the helpful AI assistant for Skill-Verse (a platform where users swap skills with 0 money).\n"
            f"User asked: {user_msg}\n"
            f"Answer concisely in friendly markdown:"
        )
        ollama_reply = query_ollama(ollama_prompt)
        if ollama_reply:
            return f"🤖 [Local Ollama Llama 3.2]:\n\n{ollama_reply}"

        # 3. Fallback if Ollama is not yet launched
        return (
            f"👋 I'm Skye! To unlock free offline conversational AI:\n"
            f"1. Download Ollama from https://ollama.com\n"
            f"2. Run in terminal: 'ollama run llama3.2:1b'\n"
            f"3. Ask me anything about skill swaps, coding, or learning roadmaps!"
        )


if __name__ == "__main__":
    agent = SkillVerseAgent()
    print("=" * 65)
    print("🤖 Skill-Verse Local AI Agent (CLI Version)")
    print("Zero API Keys Required • Connects to Local Ollama automatically")
    print("Type 'exit' to quit.")
    print("=" * 65)

    while True:
        try:
            msg = input("\n👤 You: ")
            if msg.strip().lower() in ["exit", "quit"]:
                break
            if not msg.strip():
                continue
            answer = agent.ask(msg)
            print(f"\n{answer}\n")
            print("-" * 65)
        except (KeyboardInterrupt, EOFError):
            break
