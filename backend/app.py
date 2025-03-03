# backend/app.py
# Main entry point, FastAPI setup, CORS

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback
import sqlite3
import os

from routers import clients, payments, files
from database.connection import test_connection

# Create FastAPI application
app = FastAPI(
    title="401(k) Payment Tracking System",
    description="Backend API for 401(k) payment management application",
    version="1.0.0"
)

# Add CORS middleware to allow local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(clients.router)
app.include_router(payments.router)
app.include_router(files.router)

# Exception handlers
@app.exception_handler(sqlite3.Error)
async def sqlite_exception_handler(request: Request, exc: sqlite3.Error):
    """Handle SQLite exceptions"""
    return JSONResponse(
        status_code=500,
        content={"message": f"Database error: {str(exc)}"},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    error_detail = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    print(f"Unhandled exception: {error_detail}")
    
    return JSONResponse(
        status_code=500,
        content={"message": f"An unexpected error occurred: {str(exc)}"},
    )

# Create temp OneDrive directory for development
@app.on_event("startup")
async def startup_event():
    """Run startup tasks"""
    # Ensure temp directory exists for development
    temp_dir = os.path.join(os.path.dirname(__file__), "temp_onedrive")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Test database connection
    if not test_connection():
        print("WARNING: Could not connect to database!")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "401(k) Payment Tracking System API",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Test database connection
    db_connection = test_connection()
    
    return {
        "status": "healthy" if db_connection else "unhealthy",
        "database": "connected" if db_connection else "disconnected"
    }

# Run with: uvicorn app:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)