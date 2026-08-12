from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import setup_exception_handlers
from app.core.middleware import RequestContextMiddleware

# Initialize logging before app creation
setup_logging()

from app.ai.telemetry.tracker import tracker
from app.core.llm_cache import setup_llm_cache
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_llm_cache()
    asyncio.create_task(tracker.start_listening())
    yield
    # Shutdown (cleanup if needed)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

from app.core.telemetry import setup_telemetry
from app.core.metrics import setup_metrics

# Initialize OpenTelemetry and Prometheus Metrics
setup_telemetry(app)
setup_metrics(app)

from app.core.rate_limit import limiter
from slowapi.middleware import SlowAPIMiddleware

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

from app.core.middleware import RequestContextMiddleware, OPAMiddleware

# Add Middleware
app.add_middleware(OPAMiddleware)
app.add_middleware(RequestContextMiddleware)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Add Exception Handlers
setup_exception_handlers(app)

from app.api.v1.api import api_router

# Add API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to Veridex API Platform"}
