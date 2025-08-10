from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime

ProjectType = Literal["Mechanical", "Electrical", "Civil", "Software", "Other"]

class GenerateRequest(BaseModel):
    projectName: str = Field(min_length=2, max_length=120)
    projectType: ProjectType
    description: str = Field(min_length=10, max_length=2000)
    tone: Literal["formal","concise"] = "formal"
    level: Literal["high","detailed"] = "detailed"

class RequirementItem(BaseModel):
    category: Literal["Functional","Performance","Safety","Compliance","Reliability","Maintainability","Verification"]
    text: str
    priority: Literal["MUST","SHOULD","MAY"] = "MUST"
    acceptance_criteria: List[str]
    rationale: Optional[str] = None
    standard_refs: List[str] = []

class GenerateResponse(BaseModel):
    project_name: str
    summary: str
    categories: List[str]
    requirements: List[RequirementItem]
    generated_at: datetime
