from pydantic import BaseModel
from typing import Any, Dict, Optional, Generic, TypeVar

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None

def success_response(data: Any, metadata: Optional[Dict[str, Any]] = None) -> APIResponse:
    return APIResponse(success=True, data=data, metadata=metadata)

def error_response(code: str, message: str, details: Optional[Any] = None) -> APIResponse:
    return APIResponse(
        success=False,
        error={
            "code": code,
            "message": message,
            "details": details
        }
    )
