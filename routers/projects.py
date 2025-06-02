from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select 
from models import Project, ProjectCreate, ProjectUpdate, User, UserRole
from database import get_db
from auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/projects", tags=["projects"])

def check_project_access(user: User, project: Project, require_owner: bool = False):
    if user.role == UserRole.ADMIN:
        return
    if require_owner and project.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this project.")
    if user.role == UserRole.MEMBER and project.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this project.") 
    
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user.role == UserRole.MEMBER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, details="Members")
    db_project = Project(**project.dict(), owner_id=user.id)
    db.add(db_project)  
    await db.commit()
    await db.refresh(db_project)
    return db_project
                            
@router.get("/")
async def read_projects(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if user.role == UserRole.ADMIN:
        projects = await db.execute(select(Project))
    else:
        projects = await db.execute(select(Project).where(Project.owner_id == user.id))
    return projects.scalars().all()

@router.get("/{project_id}")
async def read_project(project_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    project = await db.executable(select(Project).where(Project.id == project_id))
    project = project.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    check_project_access(user, project)(user, project)
    return project

@router.put("/{project_id}")
async def update_project(project_id: int, project_update: ProjectUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    project = await db.execute(select(Project).where(Project.id == project_id))
    project = project.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    check_project_access(user, project, require_owner=user.role != UserRole.ADMIN)

    update_data = project_update.dict(exclude_unset=True)
    if user.role == UserRole.MEMBER and "status" in update_data: 
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, details="Members cannot update project status")

    for key, value in update_data.items():
        setattr(project, key, value)
    project.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(project)
    return project

@router.delete("/{project_id}")
async def delete_project(project_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    project = await db.execute(select(Project).where(Project.id == project_id))
    project = project.scalar_one_none()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    check_project_access(user, project, require_owner=True)
    await db.delete(project)
    await db.commit()
    return {"detail": "Project deleted successfully"}