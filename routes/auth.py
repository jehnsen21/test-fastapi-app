from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from models.user_model import User, UserCreate
from models.auth_model import Token
from typing import Optional
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosHttpResponseError
from config import settings
import logging
from services.auth_service import AuthService

auth_service = AuthService()

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        return await auth_service.generate_access_token(form_data.username, form_data.password)
    except CosmosResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database not found",
        )
    
# @router.post("/register")
# async def register_user(user: UserCreate, db: CosmosClient = Depends(get_db)):
#     try:
#         container = db.get_container_client("users")
#         try:
#             await container.read_item(item=user.username, partition_key=user.username)
#             raise HTTPException(status_code=400, detail="Username already registered")
#         except CosmosResourceNotFoundError:
#             hashed_password = get_password_hash(user.password)
#             # Create a new User object with the username as id
#             db_user = User(
#                 id=user.username,  # Set id to username
#                 username=user.username,
#                 email=user.email,
#                 password=hashed_password,
#                 role=user.role
#             )
#             await container.create_item(db_user.model_dump(mode="json"))
#             return { "message": "User created successfully!" }

#     except CosmosResourceNotFoundError:
#         # logger.error(f"Database not working: {settings.COSMOS_DATABASE}")
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Database not found",
#         )

