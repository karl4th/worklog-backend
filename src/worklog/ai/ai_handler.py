import anthropic
from src.worklog.config.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from src.worklog.ai.service import AIService
from src.worklog.ai.models import *
from sqlalchemy import insert
from .whatsapp_handler import WhatsappHandler
from sqlalchemy import select
import httpx
from src.worklog.queue.service import RabbitMQPublisher

class AIHandler:
    def __init__(self, db: AsyncSession):
        self.client = anthropic.Anthropic(
            api_key="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"
        )
        self.model = "claude-3-5-sonnet-20241022"
        self.max_tokens = 1000
        self.temperature = 1
        self.db = db
        self.ai_service = AIService(db)
        self.whatsapp_handler = WhatsappHandler()
        self.rabbitmq_publisher = RabbitMQPublisher()

    async def _set_creator(self, system: str, messages: list, tools: list):
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system,
                messages=messages,
                tools=tools
            )
            return message
        except anthropic.AuthenticationError as e:
            return {"error": f"Authentication error: {str(e)}"}
        except Exception as e:
            return {"error": f"Error calling Anthropic API: {str(e)}"}
    
    async def process_agent_request(self, agent_id: int, user_id: int):
        """
        Process an agent request by getting the agent data from AIService
        and then sending it to the Anthropic API.
        
        Args:
            agent_id: The ID of the agent to use
            user_id: The ID of the user making the request
            
        Returns:
            A dictionary containing the response from the Anthropic API
        """
        # Get agent data from AIService
        agent_data = await self.ai_service._set_agent(agent_id, user_id)
        
        # Check if there was an error
        if "error" in agent_data:
            return agent_data
        
        # Extract the data needed for the Anthropic API
        system_message = agent_data["system_message"]
        messages = agent_data["messages"]
        tools = agent_data["tools"]
        
        # Send the request to the Anthropic API
        response = await self._set_creator(system_message, messages, tools)
        
        # Check if there was an error
        if "error" in response:
            return response
        
        # Process the response and save it to the database
        await self._process_response(agent_id, user_id, response)
        
        # Return a properly formatted response
        return {"response": self._extract_text_content(response)}
    
    async def _process_response(self, agent_id: int, user_id: int, response):
        """
        Process the response from the Anthropic API and save it to the database.
        This method handles both text responses and tool use responses.
        """
        # Проверяем, содержит ли ответ вызов инструмента
        tool_use = False
        tool_name = None
        tool_id = None
        tool_input = None
        text_content = ""
        
        # Обработка содержимого ответа
        if hasattr(response, 'content'):
            for content_block in response.content:
                if content_block.type == 'text':
                    text_content += content_block.text + "\n"
                elif content_block.type == 'tool_use':
                    tool_use = True
                    tool_name = content_block.name
                    tool_id = content_block.id
                    tool_input = content_block.input
                    

        await self._save_response(agent_id, user_id, text_content, tool_use, tool_name, tool_id, tool_input)
        if tool_use == True:
            await self._save_tool_use(agent_id, user_id, tool_name, tool_id, tool_input)
    
    def _extract_text_content(self, response):
        """
        Extract text content from the response.
        """
        content = ""
        if hasattr(response, 'content'):
            for block in response.content:
                if hasattr(block, 'type') and block.type == 'text':
                    content += block.text + "\n"
        return content.strip()
    
    async def _save_response(self, agent_id: int, user_id: int, content: str, tool_use: bool = False, 
                            tool_name: str = None, tool_id: str = None, tool_input: dict = None):
        """
        Save the response from the Anthropic API to the database.
        
        Args:
            agent_id: The ID of the agent
            user_id: The ID of the user
            content: The text content to save
            tool_use: Whether the response contains a tool use
            tool_name: The name of the tool used
            tool_id: The ID of the tool use
            tool_input: The input to the tool
        """
        message_record = {
            "agent_id": agent_id,
            "user_id": user_id,
            "content": content,
            "type_message": "text",
            "role": "assistant",
            "tool_use": tool_use,
            "tool_name": tool_name,
            "tool_id": tool_id,
            "tool_input": tool_input,
            "tool_output": None,
        }
        
        await self.db.execute(
            insert(AgentMessages),
            [message_record]
        )
        await self.db.commit()
        chat_id = await self.ai_service._get_user_connection(user_id)
        data = await self.whatsapp_handler.send_message(content, chat_id)
    
    async def _save_tool_use(self, agent_id: int, user_id: int, tool_name: str, tool_id: str, tool_input: dict):
        """
        Execute a tool by making an HTTP request to the specified URL and save the response to the database.
        
        Args:
            agent_id: The ID of the agent
            user_id: The ID of the user
            tool_name: The name of the tool used
            tool_id: The ID of the tool use
            tool_input: The input to the tool (will be used as request body or params)
        """
        # Get the tool details from the database
        tools_db = await self.db.execute(
            select(AgentToolsData).where(
                AgentToolsData.agent_id == agent_id,
                AgentToolsData.tool_name == tool_name
            )
        )
        tool = tools_db.scalars().first()
        
        if not tool:
            return {"error": f"Tool {tool_name} not found"}
        
        # Prepare the request
        url = tool.tool_url
        method = tool.tool_method.value.lower()
        headers = tool.tool_headers or {}
        body = tool_input
        
        # Execute the request
        try:
            async with httpx.AsyncClient() as client:
                if method == 'get':
                    response = await client.get(url, headers=headers, params=body)
                elif method == 'post':
                    response = await client.post(url, headers=headers, json=body)
                elif method == 'put':
                    response = await client.put(url, headers=headers, json=body)
                elif method == 'delete':
                    response = await client.delete(url, headers=headers, params=body)
                else:
                    return {"error": f"Unsupported method: {method}"}
                
                # Get the response data
                response_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                
                # Save the tool use and response to the database
                message_record = {
                    "agent_id": agent_id,
                    "user_id": user_id,
                    "content": f"tool",
                    "type_message": "tool_result",
                    "role": "user",
                    "tool_use": True,
                    "tool_name": tool_name,
                    "tool_id": tool_id,
                    "tool_input": tool_input,
                    "tool_output": response_data,
                }
                
                await self.db.execute(
                    insert(AgentMessages),
                    [message_record]
                )
                await self.db.commit()
                
                # Send the response to the user via WhatsApp
                self.rabbitmq_publisher.send({
                    "chat_id": user_id,
                    "message": "new"
                })                
                
                return {"success": True, "response": response_data}
                
        except Exception as e:
            error_message = f"Error executing tool {tool_name}: {str(e)}"
            
            # Save the error to the database
            message_record = {
                "agent_id": agent_id,
                "user_id": user_id,
                "content": error_message,
                "type_message": "tool",
                "role": "assistant",
                "tool_use": True,
                "tool_name": tool_name,
                "tool_id": tool_id,
                "tool_input": tool_input,
                "tool_output": {"error": str(e)},
            }
            
            await self.db.execute(
                insert(AgentMessages),
                [message_record]
            )
            await self.db.commit()
            
            # Send the error to the user via WhatsApp
            chat_id = await self.ai_service._get_user_connection(user_id)
            await self.whatsapp_handler.send_message(error_message, chat_id)
            
            return {"error": error_message}


