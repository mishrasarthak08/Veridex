from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import setup_exception_handlers
from app.core.middleware import RequestContextMiddleware

# Initialize logging before app creation
setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Add Middleware
app.add_middleware(RequestContextMiddleware)

# Add Exception Handlers
setup_exception_handlers(app)

from app.api.v1.api import api_router

# Add API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Welcome to Veridex API Platform"}
