import json, re
import httpx
from datetime import datetime
from typing import Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from app.schemas import GenerateRequest
from app.config import settings

_JSON_FENCE = re.compile(r"\{.*\}", re.S)

SYSTEM_RULES = """You are a senior Requirements Engineer.
Write clear, testable, measurable requirements using RFC 2119 terms (MUST/SHOULD/MAY).
Output ONLY valid JSON following this schema:
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
 "generated_at": str (ISO 8601 UTC)
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
2) Each requirement includes acceptance criteria (bullet list), priority (MUST/SHOULD/MAY), and optional standard references.
3) Be specific and measurable (numbers/units).
Return JSON only.
"""

def _extract_json(txt: str) -> dict:
    # Try strict first
    try:
        return json.loads(txt)
    except Exception:
        pass
    # Try fenced extraction
    m = _JSON_FENCE.search(txt)
    if m:
        return json.loads(m.group(0))
    raise ValueError("Model did not return valid JSON")

class HFProvider:
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    async def generate(self, payload: GenerateRequest) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {settings.hf_api_token}",
            "Accept": "application/json",
        }
        data = {
            "inputs": f"{SYSTEM_RULES}\n\n{_user_prompt(payload)}",
            "parameters": {
                "max_new_tokens": 1200,
                "temperature": 0.3,
                "return_full_text": False,
            },
        }
        url = f"https://api-inference.huggingface.co/models/{settings.hf_model_id}"
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, headers=headers, json=data)
            r.raise_for_status()
            out = r.json()
            # HF can return either a list of {generated_text} or a dict
            if isinstance(out, list) and out and "generated_text" in out[0]:
                txt = out[0]["generated_text"]
            elif isinstance(out, dict) and "generated_text" in out:
                txt = out["generated_text"]
            else:
                txt = json.dumps(out)
        obj = _extract_json(txt)
        obj["generated_at"] = datetime.utcnow().isoformat() + "Z"
        obj["project_name"] = payload.projectName
        return obj
