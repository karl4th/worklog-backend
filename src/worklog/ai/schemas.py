from pydantic import BaseModel, Field
from datetime import datetime
from .models import Language, Model, ToolType, ToolMethod
from typing import Optional


class CreateAIAgent(BaseModel):
    name: str = Field(..., example="Aibek")
    description: str = Field(..., example="Описание")
    system_message: str = Field(..., example="Системное сообщение")
    language: Language = Field(..., example="kazakh")
    additional_instructions: str = Field(..., example="russian")
    model: Model = Field(..., example="claude_3_5_sonnet")
    is_active: bool = Field(..., example="True")


class CreateAgentTools(BaseModel):
    tool_name: str = Field(..., example="get_time")
    tool_description: str = Field(..., example="Get the current time in a specific location")
    tool_properties: dict = Field(..., example={"location": {"type": "string", "description": "The location to get the time in"}})
    tool_required: list = Field(..., example=["location"])
    tool_type: ToolType = Field(..., example="webhook")
    tool_method: ToolMethod = Field(..., example="get")
    tool_url: str = Field(..., example="https://api.example.com/api/v1/ai/webhook")
    tool_headers: dict = Field(..., example={"Content-Type": "application/json"})
    tool_body: dict = Field(..., example={"key": "value"})


class AgentToolsResponse(BaseModel):
    id: int
    agent_id: int
    tool_name: str
    tool_description: str
    tool_properties: dict
    tool_required: list

    tool_type: ToolType
    tool_method: ToolMethod
    tool_url: str
    tool_headers: Optional[dict] = None
    tool_body: Optional[dict] = None


class AgentResponse(BaseModel):
    id: int
    name: str
    description: str
    system_message: str
    model: Model
    tools: Optional[list[AgentToolsResponse]] = None
