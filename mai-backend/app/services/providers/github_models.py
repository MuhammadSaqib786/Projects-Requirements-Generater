import json, re
from datetime import datetime
from typing import Dict, Any, List

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

from app.schemas import GenerateRequest
from app.config import settings

_CODE_FENCE_START = re.compile(r"^```(?:json)?\s*", re.I)
_CODE_FENCE_END = re.compile(r"\s*```$", re.I)


SYSTEM_RULES = """You are a senior Requirements Engineer.
Write clear, testable, measurable requirements using RFC 2119 terms (MUST/SHOULD/MAY).
Return ONLY valid JSON that matches the schema below. Do NOT include any extra text, prose, or markdown fences.

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
    # try direct
    try:
        return json.loads(s)
    except Exception:
        pass
    # try to grab the largest {...} window
    first = s.find("{")
    last = s.rfind("}")
    if first != -1 and last != -1 and last > first:
        try:
            return json.loads(s[first:last+1])
        except Exception:
            pass
    preview = s[:400].replace("\n", " ")
    raise ValueError(f"Model output was not JSON. Preview: {preview!r}")

class GitHubModelsProvider:
    """Provider that calls GitHub Models via Azure AI Inference SDK (DeepSeek-V3-0324)."""

    def __init__(self) -> None:
        if not settings.github_token:
            raise RuntimeError("GITHUB_TOKEN not configured")
        self.client = ChatCompletionsClient(
            endpoint=settings.github_endpoint,
            credential=AzureKeyCredential(settings.github_token),
        )
        self.model = settings.github_model_id

    def _complete(self, messages: List, max_tokens: int = 3200):
        # SDK is sync; fine for our usage.
        return self.client.complete(
            messages=messages,
            temperature=0.2,
            top_p=0.9,
            max_tokens=max_tokens,  # more room to avoid truncation
            model=self.model,
        )

    async def generate(self, payload: GenerateRequest) -> Dict[str, Any]:
        # ---- First attempt: full generation
        messages = [
            SystemMessage(SYSTEM_RULES),
            UserMessage(_user_prompt(payload)),
        ]
        try:
            resp = self._complete(messages, max_tokens=3200)
            text = resp.choices[0].message.content if resp.choices else ""
            try:
                obj = _parse_or_raise(text)
            except ValueError:
                # ---- Second attempt: repair pass
                repair_messages = [
                    SystemMessage(
                        "You repair malformed JSON. Return ONLY valid JSON, no markdown, matching the given schema."
                    ),
                    UserMessage(
                        "Fix and return as valid JSON only:\n\n" + _strip_fences(text)
                    ),
                ]
                repair = self._complete(repair_messages, max_tokens=2000)
                repaired_text = repair.choices[0].message.content if repair.choices else ""
                obj = _parse_or_raise(repaired_text)
        except Exception as e:
            raise RuntimeError(f"GitHub Models request failed: {repr(e)}") from e

        # ensure required fields
        obj.setdefault("project_name", payload.projectName)
        obj["generated_at"] = datetime.utcnow().isoformat() + "Z"
        if not obj.get("categories") and obj.get("requirements"):
            obj["categories"] = sorted({r.get("category", "Uncategorized") for r in obj["requirements"]})
        return obj
