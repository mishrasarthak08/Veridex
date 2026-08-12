from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
import uuid

from app.db.session import get_db
from app.api.deps import get_current_user
from app.db.models.user import User
from pydantic import BaseModel
from app.core.rate_limit import limiter
from app.services.chat_service import ChatService
from app.services.retrieval_service import RetrievalService
from fastapi.responses import StreamingResponse
import json
import litellm
import asyncio

router = APIRouter()

class ChatMessageCreate(BaseModel):
    thread_id: str
    role: str
    content: str
    traces: list = []

@router.get("/")
async def chat_status():
    return {"status": "ok", "message": "Chat service is running"}

@router.get("/threads")
async def get_chat_threads(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve all unique chat threads for the current user, ordered by most recently updated.
    """
    service = ChatService(db)
    return await service.get_user_threads(current_user.id)


@router.get("/history/{thread_id}")
async def get_chat_history(
    thread_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve chat history for a specific thread_id.
    """
    service = ChatService(db)
    return await service.get_thread_history(thread_id, current_user.id)

@router.post("/message")
@limiter.limit("20/minute")
async def add_chat_message(
    request: Request,
    message_in: ChatMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Save a new chat message to history.
    """
    service = ChatService(db)
    return await service.add_message(
        thread_id=message_in.thread_id,
        role=message_in.role,
        content=message_in.content,
        traces=message_in.traces,
        user_id=current_user.id
    )

@router.post("/stream")
@limiter.limit("20/minute")
async def chat_stream(
    request: Request,
    message_in: ChatMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ChatService(db)
    
    # Save user message
    await service.add_message(
        thread_id=message_in.thread_id,
        role=message_in.role,
        content=message_in.content,
        traces=message_in.traces,
        user_id=current_user.id
    )

    async def stream_generator():
        from app.agents.execution.engine import AgentExecutor
        executor = AgentExecutor(
            workspace_id="chat_session", 
            tenant_id=str(current_user.tenant_id),
            model_name="gemini/gemini-2.5-flash"
        )
        
        queue = asyncio.Queue()
        
        async def event_callback(event_type: str, data: dict):
            await queue.put((event_type, data))
            
        async def run_agent():
            try:
                final_answer = await executor.execute_task(message_in.content, event_callback)
                await queue.put(("DONE", final_answer))
            except Exception as e:
                await queue.put(("ERROR", str(e)))
                
        # Start the agent task in the background
        agent_task = asyncio.create_task(run_agent())
        
        traces = []
        full_content = ""
        
        try:
            while True:
                event_type, data = await queue.get()
                if event_type == "DONE":
                    full_content = data
                    # Send final answer
                    yield f"data: {json.dumps({'event': 'task_completed', 'task_id': 'generation', 'result': data})}\\n\\n"
                    break
                elif event_type == "ERROR":
                    yield f"data: {json.dumps({'event': 'task_failed', 'task_id': 'generation', 'error': data})}\\n\\n"
                    break
                else:
                    yield f"data: {json.dumps({'event': event_type, **data})}\\n\\n"
                    if event_type == "task_completed" and "Tool:" in data.get("task_id", ""):
                        traces.append({"message": f"Used {data['task_id']} - Result length: {len(str(data.get('result', '')))}", "type": "tool"})
                        
            await service.add_message(
                thread_id=message_in.thread_id,
                role="assistant",
                content=full_content,
                traces=traces,
                user_id=current_user.id
            )
        except asyncio.CancelledError:
            print("Stream cancelled by client")
            agent_task.cancel()
            raise
        except Exception as e:
            print(f"Error in chat stream: {e}")
            yield f"data: {json.dumps({'event': 'task_failed', 'task_id': 'generation', 'error': str(e)})}\\n\\n"
            
    return StreamingResponse(stream_generator(), media_type="text/event-stream")
