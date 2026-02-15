"""
FastAPI main application entry point.
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, members, events, announcements, worship_files, worship_repertoire, worship_schedule
import os
import sys

# Seed dev admin on startup if DEV_MODE=true
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'execution'))
from auth.seed_dev_admin import seed_dev_admin

app = FastAPI(
    title="Church Agenda API",
    description="REST API for Church Management System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed dev admin on startup
@app.on_event("startup")
async def startup_event():
    seed_dev_admin()

# Include routers
app.include_router(auth.router)
app.include_router(members.router)
app.include_router(events.router)
app.include_router(announcements.router)
app.include_router(worship_files.router)
app.include_router(worship_repertoire.router)
app.include_router(worship_schedule.router)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"ok": True, "data": {"message": "Church Agenda API is running"}, "error_key": None}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"ok": True, "data": {"status": "healthy"}, "error_key": None}
