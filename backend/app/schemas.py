from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, ConfigDict

class DepartmentOut(BaseModel):
    id: int
    code: str
    name: str
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class WorkflowCreate(BaseModel):
    name: str = Field(min_length=3, max_length=160)
    department_id: int
    description: str = Field(default="", max_length=5000)
    trigger_type: Literal["manual", "scheduled", "event"] = "manual"
    definition: dict[str, Any] = Field(default_factory=dict)

class WorkflowOut(BaseModel):
    id: int
    name: str
    department_id: int
    description: str
    status: str
    trigger_type: str
    definition: dict[str, Any]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RunOut(BaseModel):
    id: int
    workflow_id: int
    status: str
    message: str
    result: dict[str, Any]
    model_config = ConfigDict(from_attributes=True)
