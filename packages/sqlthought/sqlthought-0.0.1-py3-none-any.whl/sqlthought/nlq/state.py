from typing import Optional, Any
from pydantic import BaseModel


class PipelineState(BaseModel):
    question: Optional[str] = None
    db_path: Optional[str] = None
    schema: Optional[str] = None

    schema_output: Optional[str] = None
    subproblem_output: Optional[str] = None
    plan_output: Optional[str] = None

    sql: Optional[str] = None
    success: Optional[bool] = None
    result: Optional[Any] = None

    correction_plan: Optional[str] = None
    correction_attempt: int = 0
