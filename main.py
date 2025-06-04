from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from routers import projects, users, auth
import logging

# Import or define CosmosClientSingleton
from database import CosmosClientSingleton

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the application...")
    try:
        await init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise e
    yield
    logger.info("Shutting down the application...")

    try:
        client = CosmosClientSingleton()
        await client.close()
        logger.info("database connection closed successfully.")
    except Exception as e:
        logger.error(f"Failed to close database connection: {str(e)}")

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
app.include_router(users.router, prefix="/api/v1") 


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
