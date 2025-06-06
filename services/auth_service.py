# project-management-api/services/user_service.py
from fastapi import HTTPException, Depends, status
from azure.cosmos.aio import CosmosClient
from passlib.context import CryptContext
from models.user_model import User
from models.user_model import UserCreate, UserResponse
from models.enums import UserRole
from services.cosmos_service import CosmosService
from fastapi.security import OAuth2PasswordBearer
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from jose import JWTError, jwt
from config import settings
from datetime import datetime, timedelta
from typing import Optional
import logging


logger = logging.getLogger(__name__)
SECRET_KEY = settings.COSMOS_KEY
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

class AuthService(CosmosService[User]):

    def __init__(self):
        super().__init__(User, container_name="users", partition_key_path="/username")

    async def pre_create_user(self, user: User) -> User:
        existing_user = await self.get_user(user.username)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
        user.hashed_password = pwd_context.hash(user.password)
        return user

    async def create_user(self, user: UserCreate) -> UserResponse:
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=user.password,  # Will be hashed in pre_create
            role=user.role,
            created_at=datetime.now(datetime.timezone.utc),
        )
        created_user = await self.create(db_user, user.username)
        return UserResponse(**created_user.model_dump())

    async def get_user(self, username: str) -> User | None:
        try:
            container = await self.get_container()
            query = "SELECT * FROM c WHERE c.username = @username"
            parameters = [{"name": "@username", "value": username}]
            async for item in container.query_items(query=query, parameters=parameters, enable_cross_partition_query=True):
                return User(**item)
            return None
        except Exception as e:
            logger.error(f"Error fetching user {username}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}")
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool :
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(password):
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta]=None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def get_current_user(self, token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Could not validate credentials",
            headers = {"WWW-Authenticate" : "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        try:
            container = await self.get_container()
            user = await container.read_item(item=username, partition_key=username)
            return User(**user)
        except CosmosResourceNotFoundError:
            raise credentials_exception
        
    async def generate_access_token(self, username: str, password: str) -> User | None:
        # async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: CosmosClient = Depends(get_db)):
        print(f"=== LOGIN ATTEMPT DEBUG ===")
        print(f"Username received: '{username}'")
        print(f"Password received: '{password}' (length: {len(password) if password else 0})")
        
        if not username or not password:
            print("ERROR: Username or password is empty!")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username and password are required"
            )
        
        try:
        
            print(f"Looking up user: '{username}'")
        
            try:

                user_data = await self.read(username, username)
                print(f"User data retrieved: {user_data}")
            except CosmosResourceNotFoundError:
                print(f"❌ USER '{username}' NOT FOUND")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
       
            stored_hash = user_data.password
            print(f"Stored hash: {stored_hash}")
            
            if not stored_hash:
                print("ERROR: No hashed_password in user data")
                raise HTTPException(status_code=500, detail="User data corrupted")
            
            # Test password verification
            print(f"Verifying password '{password}' against hash")
            is_valid = self.verify_password(password, stored_hash)
            print(f"Password verification result: {is_valid}")
            
            if not is_valid:
                print("❌ PASSWORD VERIFICATION FAILED")
                # Let's also test what the hash should be
                expected_hash = self.get_password_hash(password)
                print(f"Expected hash for '{password}': {expected_hash}")
                
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            print("✅ PASSWORD VERIFICATION SUCCESS")
            
            # Create user object and token
            # user = User(**user_data)
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = self.create_access_token(
                data={"sub": user_data.username, "role": user_data.role},
                expires_delta=access_token_expires
            )
            
            print("✅ TOKEN CREATED SUCCESSFULLY")
            return {"access_token": access_token, "token_type": "bearer"}
            
        except CosmosResourceNotFoundError:
            print(f"❌ USER '{username}' NOT FOUND")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

