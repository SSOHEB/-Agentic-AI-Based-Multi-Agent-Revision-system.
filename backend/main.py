from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.firebase import lifespan
# We import the routers below. Note: These router modules will be completely empty when we create them.
from backend.routers import (
    auth,
    profile,
    onboarding,
    topics,
    sessions,
    progress,
    notifications,
    internal
)
from backend.routers.user_router import router as user_router

# Initialize the FastAPI app with the lifespan event handler (which initializes Firebase)
app = FastAPI(
    title="Smart Revision API",
    description="Backend API for the Smart Revision platform.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS Middleware
# In production, replace allow_origins=["*"] with your actual frontend domain(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all Routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(onboarding.router)
app.include_router(topics.router)
app.include_router(sessions.router)
app.include_router(progress.router)
app.include_router(notifications.router)
app.include_router(internal.router)
app.include_router(user_router)


@app.get("/", tags=["Health"])
async def health_check():
    """
    Simple health check endpoint to verify the API is up and running.
    """
    return {
        "status": "ok",
        "service": "smart-revision-backend"
    }
