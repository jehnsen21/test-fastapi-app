from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from models import User, UserCreate, Token
from database import get_db
from typing import Optional
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = settings.COSMOS_KEY
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool :
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta]=None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: CosmosClient = Depends(get_db)):
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
        container = db.get_container_client("users")
        user = await container.read_item(item=username, partition_key=username)
        return User(**user)
    except CosmosResourceNotFoundError:
        raise credentials_exception

# @router.post("/token", response_model=Token)
# async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: CosmosClient = Depends(get_db)):
#     try:
#         container = db.get_container_client("users")
#         user_data = await container.read_item(item=form_data.username, partition_key=form_data.username)
#         print("form data: ", form_data)
#         print(f"Raw user data from DB: {user_data}")
#         print(f"Available fields: {list(user_data.keys())}")


#         user = User(**user)

#         print("User found:", user.username)
#         print("Stored password hash:", user.hashed_password if hasattr(user, 'hashed_password') else user.password)
#         print("Input password:", form_data.password)

#         stored_password = user.hashed_password if hasattr(user, 'hashed_password') else user.password
#         print("Password verification result:", verify_password(form_data.password, stored_password))

#         if not user or not verify_password(form_data.password, stored_password):
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Incorrect username or password",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )
#         access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#         access_token = create_access_token(
#             data = {"sub": user.username, "role": user.role},
#             expires_delta=access_token_expires
#         )
#         return { "access_token": access_token, "token_type": "bearer"}
#     except CosmosResourceNotFoundError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: CosmosClient = Depends(get_db)):
    print(f"=== LOGIN ATTEMPT DEBUG ===")
    print(f"Username received: '{form_data.username}'")
    print(f"Password received: '{form_data.password}' (length: {len(form_data.password) if form_data.password else 0})")
    
    if not form_data.username or not form_data.password:
        print("ERROR: Username or password is empty!")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required"
        )
    
    try:
        container = db.get_container_client("users")
        print(f"Looking up user: '{form_data.username}'")
       
        try:
            user_data = await container.read_item(item=form_data.username, partition_key=form_data.username)
            print(f"User data retrieved: {user_data.get('username')}")
        except CosmosResourceNotFoundError:
            print(f"❌ USER '{form_data.username}' NOT FOUND")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        stored_hash = user_data.get('password')
        print(f"Stored hash: {stored_hash}")
        
        if not stored_hash:
            print("ERROR: No hashed_password in user data")
            raise HTTPException(status_code=500, detail="User data corrupted")
        
        # Test password verification
        print(f"Verifying password '{form_data.password}' against hash")
        is_valid = verify_password(form_data.password, stored_hash)
        print(f"Password verification result: {is_valid}")
        
        if not is_valid:
            print("❌ PASSWORD VERIFICATION FAILED")
            # Let's also test what the hash should be
            expected_hash = get_password_hash(form_data.password)
            print(f"Expected hash for '{form_data.password}': {expected_hash}")
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        print("✅ PASSWORD VERIFICATION SUCCESS")
        
        # Create user object and token
        user = User(**user_data)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role},
            expires_delta=access_token_expires
        )
        
        print("✅ TOKEN CREATED SUCCESSFULLY")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except CosmosResourceNotFoundError:
        print(f"❌ USER '{form_data.username}' NOT FOUND")
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


@router.post("/register")
async def register_user(user: UserCreate, db: CosmosClient = Depends(get_db)):
    try:
        container = db.get_container_client("users")
        try:
            await container.read_item(item=user.username, partition_key=user.username)
            raise HTTPException(status_code=400, detail="Username already registered")
        except CosmosResourceNotFoundError:
            hashed_password = get_password_hash(user.password)
            # Create a new User object with the username as id
            db_user = User(
                id=user.username,  # Set id to username
                username=user.username,
                email=user.email,
                password=hashed_password,
                role=user.role
            )
            await container.create_item(db_user.model_dump(mode="json"))
            return { "message": "User created successfully!" }

    except CosmosResourceNotFoundError:
        # logger.error(f"Database not working: {settings.COSMOS_DATABASE}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database not found",
        )



# Add this test endpoint to verify password hashing is working
@router.post("/test-password")
async def test_password_verification(request: dict):
    """Test endpoint to verify password hashing"""
    password = request.get("password")
    stored_hash = "$2b$12$q52h7uV.TEA.osn.zQuul.ewFC/GjdPTSDq/c2UzsmzPJdFDOnsuw"
    
    print(f"Testing password: '{password}'")
    print(f"Against hash: {stored_hash}")
    
    result = verify_password(password, stored_hash)
    print(f"Verification result: {result}")
    
    # Also test creating a new hash
    new_hash = get_password_hash(password)
    print(f"New hash would be: {new_hash}")
    
    return {
        "password": password,
        "stored_hash": stored_hash,
        "verification_result": result,
        "new_hash": new_hash
    }