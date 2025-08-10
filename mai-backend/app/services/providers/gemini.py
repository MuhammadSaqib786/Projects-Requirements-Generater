import json, re
from datetime import datetime
from typing import Dict, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from app.schemas import GenerateRequest
from app.config import settings

JSON_RE = re.compile(r"\{.*\}\s*$", re.S)

SYSTEM_RULES = """You are a senior Requirements Engineer.
Write clear, testable, measurable requirements using RFC 2119 terms (MUST/SHOULD/MAY).
Return ONLY valid JSON matching this schema:
{
 "project_name": str,
 "summary": str,
 "categories": [str],
 "requirements": [
   {
     "category": "Functional"|"Performance"|"Safety"|"Compliance"|"Reliability"|"Maintainability"|"Verification",
     "text": str,
     "priority": "MUST"|"SHOULD"|"MAY",
     "acceptance_criteria": [str],
     "rationale": str|null,
     "standard_refs": [str]
   }
 ],
 "generated_at": str
}
"""

def _user_prompt(p: GenerateRequest) -> str:
    return f"""Project Name: {p.projectName}
Project Type: {p.projectType}
Tone: {p.tone}; Level: {p.level}

Brief:
{p.description}

Tasks:
1) Create 25–45 requirements across categories (Functional, Performance, Safety, Compliance, Reliability, Maintainability, Verification).
2) Each requirement MUST include acceptance_criteria (bullet list), priority (MUST/SHOULD/MAY), and optional standard_refs.
3) Be specific and measurable (numbers/units).
Return JSON only.
"""

def _extract_json(txt: str) -> dict:
    try:
        return json.loads(txt)
    except Exception:
        m = JSON_RE.search(txt or "")
        if m:
            return json.loads(m.group(0))
        raise ValueError(f"Gemini text was not valid JSON. First 200 chars: {txt[:200]!r}")

class GeminiProvider:
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=6))
    async def generate(self, payload: GenerateRequest) -> Dict[str, Any]:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY not configured")

        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{settings.gemini_model_id}:generateContent?key={settings.gemini_api_key}")

        body = {
            "contents": [{
                "role": "user",
                "parts": [{"text": _user_prompt(payload)}],
            }],
            # IMPORTANT: role must be "system" here
            "system_instruction": {
                "role": "system",
                "parts": [{"text": SYSTEM_RULES}]
            },
            "generationConfig": {
                "temperature": 0.2,
                "topP": 0.9,
                "topK": 40,
                "maxOutputTokens": 1200,
                "response_mime_type": "application/json",
            },
        }

        async with httpx.AsyncClient(timeout=90) as client:
            r = await client.post(url, json=body, headers={"Content-Type": "application/json"})
            if r.status_code >= 400:
                # Surface Gemini’s real error in FastAPI response
                raise RuntimeError(f"[Gemini {r.status_code}] {r.text}")

            data = r.json()
            candidates = data.get("candidates") or []
            if not candidates:
                raise RuntimeError(f"Empty Gemini response: {data}")
            parts = candidates[0].get("content", {}).get("parts", [])
            txt = (parts[0].get("text") if parts else "") or ""
            obj = _extract_json(txt)

            obj.setdefault("project_name", payload.projectName)
            obj["generated_at"] = datetime.utcnow().isoformat() + "Z"
            if not obj.get("categories") and obj.get("requirements"):
                obj["categories"] = sorted({r.get("category","Uncategorized") for r in obj["requirements"]})
            return obj
