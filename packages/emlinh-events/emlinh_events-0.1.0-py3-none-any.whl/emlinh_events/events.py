from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator

class EventChannel(str, Enum):
    INTENT_DETECTED = "orchestrator.intent.detected"
    WORKFLOW_STATUS = "orchestrator.workflow.status"
    JOB_PROGRESS = "orchestrator.job.progress"
    CONTROL_CANCEL = "orchestrator.control.cancel"
    CONTROL_RETRY = "orchestrator.control.retry"
    AGENT_OUTPUT = "orchestrator.agent.output"

class BaseEvent(BaseModel):
    channel: EventChannel = Field(...)
    emitted_at: datetime = Field(default_factory=datetime.utcnow)
    model_config = {"str_strip_whitespace": True, "use_enum_values": True, "frozen": True}

class IntentType(str, Enum):
    RESEARCH = "research"
    PRESENTATION = "presentation"
    GENERIC = "generic"

class IntentDetected(BaseEvent):
    channel: Literal[EventChannel.INTENT_DETECTED] = EventChannel.INTENT_DETECTED
    session_id: str = Field(..., min_length=1)
    user_id: Optional[str] = Field(default=None)
    intent_type: IntentType = Field(...)
    text: str = Field(..., min_length=1)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    @field_validator("text")
    @classmethod
    def _ensure_trimmed(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("text must not be empty")
        return trimmed

class WorkflowStage(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    CANCELING = "canceling"

class WorkflowStatus(BaseEvent):
    channel: Literal[EventChannel.WORKFLOW_STATUS] = EventChannel.WORKFLOW_STATUS
    workflow_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    template_id: str = Field(..., min_length=1)
    stage: WorkflowStage = Field(...)
    progress: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    message: Optional[str] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class JobEventType(str, Enum):
    STARTED = "started"
    PROGRESS = "progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"

class JobEvent(BaseEvent):
    channel: Literal[EventChannel.JOB_PROGRESS] = EventChannel.JOB_PROGRESS
    job_id: str = Field(..., min_length=1)
    workflow_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    agent: str = Field(..., min_length=1)
    event_type: JobEventType = Field(...)
    progress: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    details: Dict[str, Any] = Field(default_factory=dict)
    @model_validator(mode='before')
    @classmethod
    def _validate_progress(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        event_type = values.get("event_type")
        progress = values.get("progress")
        if event_type in {JobEventType.COMPLETED, JobEventType.CANCELED} and progress is None:
            values["progress"] = 100.0 if event_type == JobEventType.COMPLETED else 0.0
        return values

class ControlCancel(BaseEvent):
    channel: Literal[EventChannel.CONTROL_CANCEL] = EventChannel.CONTROL_CANCEL
    workflow_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    requested_by: str = Field(..., min_length=1)
    reason: Optional[str] = Field(default=None)

class ControlRetry(BaseEvent):
    channel: Literal[EventChannel.CONTROL_RETRY] = EventChannel.CONTROL_RETRY
    workflow_id: str = Field(..., min_length=1)
    job_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    requested_by: str = Field(..., min_length=1)
    reason: Optional[str] = Field(default=None)

class AgentOutput(BaseEvent):
    channel: Literal[EventChannel.AGENT_OUTPUT] = EventChannel.AGENT_OUTPUT
    workflow_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    agent_name: str = Field(..., min_length=1)
    output_text: str = Field(...)
    is_streaming: bool = Field(default=True)
    is_final: bool = Field(default=False)
    metadata: Dict[str, Any] = Field(default_factory=dict)