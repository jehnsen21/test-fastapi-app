from fastapi import APIRouter, Depends, HTTPException, status
from models.user_model import User, UserCreate, UserRole
from database import get_db
from routes.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# @router.get("/")
# async def read_users(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
#     if user.role != UserRole.ADMIN:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, details="Admin access required")
#     users = await db.executable(select(User))
#     return users.scalars().all()