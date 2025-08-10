from datetime import datetime
from typing import Dict, Any
from app.schemas import GenerateRequest

class DummyProvider:
    async def generate(self, payload: GenerateRequest) -> Dict[str, Any]:
        # Simple, deterministic sample so the frontend can be built immediately.
        name = payload.projectName
        t = payload.projectType
        desc = payload.description[:180] + ("..." if len(payload.description) > 180 else "")

        reqs = [
            {
                "category": "Functional",
                "text": "The system SHALL capture all key project inputs and produce a structured requirement set.",
                "priority": "MUST",
                "acceptance_criteria": [
                    "Given a valid brief, when generation runs, then at least 20 requirements are produced.",
                    "Output conforms to JSON schema without errors."
                ],
                "rationale": "Ensure baseline capability.",
                "standard_refs": []
            },
            {
                "category": "Performance",
                "text": "Generation time SHOULD not exceed 6 seconds for a 500-word brief.",
                "priority": "SHOULD",
                "acceptance_criteria": [
                    "Average p95 latency ≤ 6s measured over 30 runs."
                ],
                "rationale": "Good UX.",
                "standard_refs": []
            },
            {
                "category": "Compliance",
                "text": f"The solution SHALL reference domain standards relevant to {t} projects where applicable.",
                "priority": "MUST",
                "acceptance_criteria": [
                    "At least two standards cited when applicable."
                ],
                "standard_refs": []
            }
        ]

        return {
            "project_name": name,
            "summary": f"Initial draft for a {t} project based on the brief: {desc}",
            "categories": sorted({r["category"] for r in reqs}),
            "requirements": reqs,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
