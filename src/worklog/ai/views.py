from fastapi import APIRouter, Depends, HTTPException
from src.worklog.ai.service import AIService
from src.worklog.db.core import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.worklog.ai.schemas import *
from .webhook_schema import *
from .ai_handler import AIHandler
from .whatsapp_handler import WhatsappHandler
from src.worklog.config.auth import auth


router = APIRouter(prefix="/api/v1/ai", tags=["AI - artificial-intelligence"])

@router.post("/user/connect/{chat_id}")
async def connect_user(chat_id: str, db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_user_data_dependency())):
    return await AIService(db)._create_user_connection(int(current_user['sub']), chat_id)

@router.post("/webhook", response_model=dict)
async def webhook(payload: WebhookPayload, db: AsyncSession = Depends(get_db)):
    return await AIService(db).webhook(payload)

@router.get('/user/check-connection', response_model=dict)
async def check_connection(db: AsyncSession = Depends(get_db), current_user = Depends(auth.get_user_data_dependency())):
    data = await AIService(db)._get_user_connection(int(current_user['sub']))
    return {"status": "success", "data": data}


@router.post("/create-ai-agent", response_model=dict)
async def create_ai_agent(ai_agent: CreateAIAgent, db: AsyncSession = Depends(get_db)):
    return await AIService(db).create_ai_agent(ai_agent)

@router.get("/get-ai-agent", response_model=dict)
async def get_ai_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    return await AIService(db).get_ai_agent(agent_id)

@router.put("/update-ai-agent", response_model=dict)
async def update_ai_agent(agent_id: int, ai_agent: CreateAIAgent, db: AsyncSession = Depends(get_db)):
    return await AIService(db).update_ai_agent(agent_id, ai_agent)


@router.post("/create-agent-tools", response_model=dict)
async def create_agent_tools(agent_id: int, agent_tools: CreateAgentTools, db: AsyncSession = Depends(get_db)):
    return await AIService(db).create_agent_tools(agent_id, agent_tools)

@router.put("/update-agent-tools", response_model=dict)
async def update_agent_tools(agent_id: int, agent_tools: CreateAgentTools, db: AsyncSession = Depends(get_db)):
    return await AIService(db).update_agent_tools(agent_id, agent_tools)

@router.delete("/delete-agent-tools", response_model=dict)
async def delete_agent_tools(agent_tools_id: int, db: AsyncSession = Depends(get_db)):
    return await AIService(db).delete_agent_tools(agent_tools_id)

@router.get("/get-agent-tools", response_model=dict)
async def get_agent_tools(agent_id: int, db: AsyncSession = Depends(get_db)):
    return await AIService(db).get_agent_tools(agent_id)

@router.get("/set-agent", response_model=dict)
async def set_agent( db: AsyncSession = Depends(get_db)):
    return await AIService(db)._set_agent(1, 1)

@router.post("/process-agent-request", response_model=dict)
async def process_agent_request(agent_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    """
    Process an agent request by getting the agent data and sending it to the Anthropic API.
    
    Args:
        agent_id: The ID of the agent to use
        user_id: The ID of the user making the request
        
    Returns:
        The response from the Anthropic API
    """
    try:
        response = await AIHandler(db).process_agent_request(agent_id, user_id)
        
        # Check if there was an error
        if isinstance(response, dict) and "error" in response:
            raise HTTPException(status_code=500, detail=response["error"])
            
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

