import json
import urllib.request
import urllib.parse
import urllib.error
import logging
from django.conf import settings

# Import Global Skill Data Knowledge Base (Tech, Creative, Business, Health, Trades, etc.)
try:
    from Skill_Data import query_skill_bank_data
except ImportError:
    def query_skill_bank_data(p): return ""

logger = logging.getLogger(__name__)


def call_ollama_ai(prompt, model="llama3.2:1b", image_data=None):
    """
    Call Local Ollama API (100% Offline, Free, Zero API Keys!).
    Runs on http://localhost:11434/api/generate
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 400
        }
    }

    if image_data and "base64," in image_data:
        try:
            b64_data = image_data.split("base64,")[1]
            payload["images"] = [b64_data]
            payload["model"] = "llava" # Vision model if available
        except Exception:
            pass

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')

    with urllib.request.urlopen(req, timeout=25) as response:
        res_data = json.loads(response.read().decode('utf-8'))
        text = res_data.get('response', '').strip()
        if text:
            return text
    raise ValueError("Ollama returned empty response")


def call_pollinations_ai(prompt):
    """Call Pollinations GET AI text endpoint."""
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://text.pollinations.ai/{encoded_prompt}"
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0'},
        method='GET'
    )
    with urllib.request.urlopen(req, timeout=12) as response:
        text = response.read().decode('utf-8').strip()
        if text:
            return text
    raise ValueError("Pollinations returned empty response")


def call_duckduckgo_ai(prompt):
    """Call DuckDuckGo Free AI chat API (No Key Required!)."""
    status_req = urllib.request.Request(
        "https://duckduckgo.com/duckchat/v1/status",
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'x-vqd-accept': '1'
        }
    )
    vqd = None
    with urllib.request.urlopen(status_req, timeout=8) as res:
        vqd = res.headers.get('x-vqd-4')

    if not vqd:
        raise ValueError("DuckDuckGo token fetch failed")

    chat_url = "https://duckduckgo.com/duckchat/v1/chat"
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }
    data = json.dumps(payload).encode('utf-8')
    chat_req = urllib.request.Request(
        chat_url,
        data=data,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Content-Type': 'application/json',
            'x-vqd-4': vqd
        },
        method='POST'
    )

    full_text = []
    with urllib.request.urlopen(chat_req, timeout=12) as res:
        for line in res:
            line_str = line.decode('utf-8').strip()
            if line_str.startswith('data: '):
                json_str = line_str[6:]
                if json_str == '[DONE]':
                    break
                try:
                    chunk = json.loads(json_str)
                    if 'message' in chunk:
                        full_text.append(chunk['message'])
                except Exception:
                    pass

    output = "".join(full_text).strip()
    if output:
        return output
    raise ValueError("DuckDuckGo returned empty response")


def call_gemini_api(prompt, api_key, image_data=None):
    """Call Google Gemini 1.5 Flash Multimodal Vision & Text API."""
    if not api_key:
        raise ValueError("Gemini API key missing")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    parts = []
    if image_data and "base64," in image_data:
        try:
            mime_type = image_data.split(";")[0].split(":")[1] if ":" in image_data else "image/jpeg"
            b64_data = image_data.split("base64,")[1]
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": b64_data
                }
            })
        except Exception as e:
            logger.warning(f"Error parsing image base64: {e}")

    parts.append({"text": prompt})
    payload = {
        "contents": [{"parts": parts}]
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')

    with urllib.request.urlopen(req, timeout=14) as response:
        res_data = json.loads(response.read().decode('utf-8'))
        return res_data['candidates'][0]['content']['parts'][0]['text']


def generate_ai_response(prompt, requested_provider="auto", image_data=None):
    """
    Generate accurate AI response with local Ollama priority, zero-fail failovers, and Skill_Data enrichment.
    """
    # 1. Fetch skill context from Skill_Data knowledge base
    skill_context = query_skill_bank_data(prompt)
    enriched_prompt = prompt
    if skill_context and "Skill-Verse supports" not in skill_context:
        enriched_prompt = f"Skill-Verse Context:\n{skill_context}\n\nUser Question: {prompt}\nPlease provide a helpful, friendly response formatted nicely in markdown."

    if image_data:
        enriched_prompt = f"[User attached an image / camera capture for analysis]\n{enriched_prompt}"

    gemini_key = getattr(settings, 'GEMINI_API_KEY', '')
    groq_key = getattr(settings, 'GROQ_API_KEY', '')

    pipeline = []

    # Priority 1: Local Ollama (Zero Key, Local PC)
    pipeline.append(("Local Ollama (Llama 3.2)", lambda p: call_ollama_ai(p, model="llama3.2:1b", image_data=image_data)))
    pipeline.append(("Local Ollama (Phi 3)", lambda p: call_ollama_ai(p, model="phi3:mini", image_data=image_data)))

    # Priority 2: Cloud API keys if configured
    if gemini_key:
        pipeline.append(("Google Gemini 1.5", lambda p: call_gemini_api(p, gemini_key, image_data=image_data)))
    if groq_key:
        pipeline.append(("Groq Llama 3", lambda p: call_groq_api(p, groq_key)))

    # Priority 3: Free Public Gateways (DuckDuckGo GPT-4o & Pollinations)
    pipeline.append(("Free AI (DuckDuckGo GPT-4o)", call_duckduckgo_ai))
    pipeline.append(("Free AI (Pollinations)", call_pollinations_ai))

    errors = []

    for name, func in pipeline:
        try:
            logger.info(f"Trying AI Provider: {name}")
            response = func(enriched_prompt)
            if response and len(response.strip()) > 0:
                return {
                    "success": True,
                    "provider_used": name,
                    "response": response,
                }
        except Exception as e:
            err_str = f"{name} Error: {str(e)}"
            logger.warning(err_str)
            errors.append(err_str)

    # Priority 4: Local Skill_Data Knowledge fallback
    if skill_context:
        fallback_res = f"### 📚 Skill-Verse Knowledge Response\n\n{skill_context}"
    else:
        fallback_res = f"Here is what I found for **'{prompt}'**:\n\nSkill-Verse connects learners worldwide to trade skills! Install & run Ollama (`ollama run llama3.2:1b`) for full offline local generation."

    return {
        "success": True,
        "provider_used": "Skill-Verse Knowledge Base",
        "response": fallback_res,
        "errors": errors
    }
