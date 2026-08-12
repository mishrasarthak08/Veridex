from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from typing import List, Dict, Any
from app.db.session import get_db
from app.api.deps import get_current_user
from app.db.models.user import User
from app.db.models.project import Project
from app.ai.swarm import swarm_engine
from pydantic import BaseModel

router = APIRouter()

class SwarmConfigPayload(BaseModel):
    nodes: list
    edges: list

@router.get("/")
async def get_projects(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    List user projects
    """
    result = await db.execute(select(Project).limit(10))
    projects = result.scalars().all()
    
    # If no projects, return a mock one for now
    if not projects:
        return {
            "data": [
                {
                    "id": "proj_123",
                    "name": "Default Workspace",
                    "description": "Your personal workspace for Veridex.",
                    "role": "Owner"
                }
            ]
        }
        
    return {
        "data": [
            {
                "id": str(p.id),
                "name": p.name,
                "description": p.description,
                "role": "Owner"
            } for p in projects
        ]
    }

@router.post("/{project_id}/swarm")
async def save_swarm_config(
    project_id: str,
    payload: SwarmConfigPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Save the React Flow swarm configuration for a project
    """
    # For now, just print it and pretend we saved it since the DB might not be fully seeded with the project
    print(f"Saving swarm config for project {project_id}: {len(payload.nodes)} nodes, {len(payload.edges)} edges")
    
    # Actual save logic if the DB was fully seeded:
    # stmt = update(Project).where(Project.id == project_id).values(swarm_config=payload.dict())
    # await db.execute(stmt)
    # await db.commit()
    
    return {"status": "success"}

@router.get("/{project_id}/swarm")
async def get_swarm_config(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the React Flow swarm configuration for a project
    """
    # For now, return a default mock graph so the Studio isn't empty
    return {
        "nodes": [
            { "id": "triage", "type": "agent", "position": { "x": 250, "y": 5 }, "data": { "label": "Triage Agent" } },
            { "id": "researcher", "type": "agent", "position": { "x": 100, "y": 100 }, "data": { "label": "Researcher Agent" } }
        ],
        "edges": [
            { "id": "e1-2", "source": "triage", "target": "researcher", "type": "smoothstep" }
        ]
    }

@router.post("/{project_id}/deploy")
async def deploy_swarm(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger the Swarm Engine to execute the saved configuration.
    """
    # In a real app we would load the config from DB here
    swarm_id = swarm_engine.trigger_swarm({"project_id": project_id})
    return {"status": "success", "swarm_id": swarm_id, "message": "Swarm deployment initiated."}

@router.post("/{project_id}/chaos")
async def deploy_swarm_chaos(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger the Swarm Engine in Chaos Mode (Intentional Failure Injection).
    """
    swarm_id = swarm_engine.trigger_swarm({"project_id": project_id, "chaos_mode": True})
    return {"status": "success", "swarm_id": swarm_id, "message": "Chaos Swarm deployment initiated."}
