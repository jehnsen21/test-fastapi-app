from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database.cosmos_client import CosmosClientSingleton
from routes import projects, users, auth
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code here
    yield
    # Shutdown code here

app = FastAPI(title="Project Management API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(projects.router, prefix="/api/v1")
# app.include_router(users.router, prefix="/api/v1") 


# Root endpoint
@app.get("/")
async def read_root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Project Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
