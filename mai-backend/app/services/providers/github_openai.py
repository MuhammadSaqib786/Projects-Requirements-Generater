import json, re
from datetime import datetime
from typing import Dict, Any, List
from openai import OpenAI

from app.schemas import GenerateRequest
from app.config import settings

# ---- helpers

_CODE_FENCE_START = re.compile(r"^```(?:json)?\s*", re.I)
_CODE_FENCE_END = re.compile(r"\s*```$", re.I)

SYSTEM_RULES = """You are a senior Requirements Engineer.
Write clear, testable, measurable requirements using RFC 2119 terms (MUST/SHOULD/MAY).
Return ONLY valid JSON that matches the schema below. Do NOT include markdown or code fences.

SCHEMA:
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
Return JSON only (no markdown).
"""

def _strip_fences(s: str) -> str:
    s = s.strip()
    s = _CODE_FENCE_START.sub("", s)
    s = _CODE_FENCE_END.sub("", s)
    return s.strip()

def _parse_or_raise(raw: str) -> dict:
    s = _strip_fences(raw)
    try:
        return json.loads(s)
    except Exception:
        first = s.find("{")
        last = s.rfind("}")
        if first != -1 and last != -1 and last > first:
            cand = s[first:last+1]
            try:
                return json.loads(cand)
            except Exception:
                pass
        preview = s[:400].replace("\n", " ")
        raise ValueError(f"Model output was not JSON. Preview: {preview!r}")

class GitHubOpenAIProvider:
    """
    Provider using OpenAI SDK pointed at GitHub Models endpoint.
    """

    def __init__(self) -> None:
        if not settings.github_token:
            raise RuntimeError("GITHUB_TOKEN not configured")
        self.client = OpenAI(
            base_url=settings.github_endpoint,
            api_key=settings.github_token,
        )
        self.model = settings.github_model_id

    def _complete(self, messages: List[dict], max_tokens: int = 3200):
        # Synchronous call – fine for our usage
        return self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=0.2,
            top_p=0.95,
            max_tokens=max_tokens,
        )

    async def generate(self, payload: GenerateRequest) -> Dict[str, Any]:
        base_msgs = [
            {"role": "system", "content": SYSTEM_RULES},
            {"role": "user", "content": _user_prompt(payload)},
        ]

        try:
            resp = self._complete(base_msgs, max_tokens=3200)
            text = resp.choices[0].message.content or ""
            try:
                obj = _parse_or_raise(text)
            except ValueError:
                # Repair pass: ask model to output valid JSON only
                repair_msgs = [
                    {"role": "system", "content": "You repair malformed JSON. Return ONLY valid JSON (no markdown)."},
                    {"role": "user", "content": "Fix and return as valid JSON only:\n\n" + _strip_fences(text)},
                ]
                repair = self._complete(repair_msgs, max_tokens=2000)
                obj = _parse_or_raise(repair.choices[0].message.content or "")
        except Exception as e:
            raise RuntimeError(f"GitHub OpenAI request failed: {repr(e)}") from e

        # Ensure required fields
        obj.setdefault("project_name", payload.projectName)
        obj["generated_at"] = datetime.utcnow().isoformat() + "Z"
        if not obj.get("categories") and obj.get("requirements"):
            obj["categories"] = sorted({r.get("category", "Uncategorized") for r in obj["requirements"]})
        return obj
