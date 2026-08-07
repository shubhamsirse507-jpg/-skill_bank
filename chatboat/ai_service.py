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
    # Step 1: Get status token
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

    # Step 2: Chat completion
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


def call_gemini_api(prompt, api_key):
    """Call Google Gemini 1.5 Flash API."""
    if not api_key:
        raise ValueError("Gemini API key missing")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')

    with urllib.request.urlopen(req, timeout=12) as response:
        res_data = json.loads(response.read().decode('utf-8'))
        return res_data['candidates'][0]['content']['parts'][0]['text']


def call_groq_api(prompt, api_key):
    """Call Groq Cloud API (Llama 3.1 8B)."""
    if not api_key:
        raise ValueError("Groq API key missing")

    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}]
    }
    data = json.dumps(payload).encode('utf-8')
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')

    with urllib.request.urlopen(req, timeout=12) as response:
        res_data = json.loads(response.read().decode('utf-8'))
        return res_data['choices'][0]['message']['content']


def call_openrouter_api(prompt, api_key):
    """Call OpenRouter Free Models API."""
    if not api_key:
        raise ValueError("OpenRouter API key missing")

    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {
        "model": "meta-llama/llama-3.1-8b-instruct:free",
        "messages": [{"role": "user", "content": prompt}]
    }
    data = json.dumps(payload).encode('utf-8')
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')

    with urllib.request.urlopen(req, timeout=12) as response:
        res_data = json.loads(response.read().decode('utf-8'))
        return res_data['choices'][0]['message']['content']


def generate_ai_response(prompt, requested_provider="auto"):
    """
    Generate accurate AI response with multi-level zero-fail failover and Skill_Data enrichment.
    """
    # 1. Fetch skill context from Skill_Data (covers tech, creative, business, health, lifestyle, trades)
    skill_context = query_skill_bank_data(prompt)
    enriched_prompt = prompt
    if skill_context and "Skill Bank supports" not in skill_context:
        enriched_prompt = f"Context from Skill Bank Global Knowledge Base:\n{skill_context}\n\nUser Question: {prompt}"

    gemini_key = getattr(settings, 'GEMINI_API_KEY', '')
    groq_key = getattr(settings, 'GROQ_API_KEY', '')
    openrouter_key = getattr(settings, 'OPENROUTER_API_KEY', '')

    pipeline = []
    if gemini_key:
        pipeline.append(("Google Gemini 1.5", lambda p: call_gemini_api(p, gemini_key)))
    if groq_key:
        pipeline.append(("Groq Llama 3", lambda p: call_groq_api(p, groq_key)))
    if openrouter_key:
        pipeline.append(("OpenRouter Llama 3", lambda p: call_openrouter_api(p, openrouter_key)))

    # Add free public gateways (no key needed!)
    pipeline.append(("Free AI (Pollinations)", call_pollinations_ai))
    pipeline.append(("Free AI (DuckDuckGo GPT-4o)", call_duckduckgo_ai))

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

    # Smart local Skill_Data fallback so questions about any skill ALWAYS get precise structured data!
    if skill_context:
        fallback_res = f"### 📚 Skill Bank Knowledge Response\n\n{skill_context}"
    else:
        fallback_res = f"Here is what I found for **'{prompt}'**:\n\nFor full live AI completions, add your API key in `settings.py`!"

    return {
        "success": True,
        "provider_used": "Skill Bank Knowledge Base",
        "response": fallback_res,
        "errors": errors
    }

