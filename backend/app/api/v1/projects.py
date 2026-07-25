from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.session import get_db
from app.api.deps import get_current_user
from app.db.models.user import User

router = APIRouter()

@router.get("/")
def get_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    """
    List user projects (Mocked for now)
    """
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
