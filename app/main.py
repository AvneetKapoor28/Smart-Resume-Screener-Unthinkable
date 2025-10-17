from fastapi import FastAPI
from app.api.v1.api import api_router

# Initialize the FastAPI application
app = FastAPI(
    title="Smart Resume Screener API",
    description="An intelligent API to screen and rank resumes against job descriptions.",
    version="1.0.0"
)

# Include the main API router
app.include_router(api_router, prefix="/api/v1")

# Add a root endpoint for health checks or simple access
@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint of the API.
    """
    return {"message": "Welcome to the Smart Resume Screener API. Go to /docs for documentation."}
