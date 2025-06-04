from fastapi import APIRouter, Depends, HTTPException, status
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosHttpResponseError
from models.project_model import Project, ProjectCreate, ProjectUpdate
from models.user_model import User
from models.enums import UserRole
from database import get_db
from routes.auth import get_current_user
from datetime import datetime
from uuid import uuid4
import json

router = APIRouter(prefix="/projects", tags=["projects"])

def check_project_access(user: User, project: Project, require_owner: bool = False):
    if user.role == UserRole.ADMIN:
        return
    if require_owner and project.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this project.")
    if user.role == UserRole.MEMBER and project.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this project.") 
    
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate, user: User = Depends(get_current_user), db: CosmosClient = Depends(get_db)):
    if user.role == UserRole.MEMBER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, details="Members")
    try:
        container = db.get_container_client("projects")
        db_project_data = project.dict(exclude_unset=True)  # Include only provided fields
        db_project = Project(
            id=str(uuid4()),
            owner_id=user.id,  # Set from authenticated user
            **db_project_data  # Unpack payload fields (e.g., title, description, etc.)
        )
        # Convert to JSON-serializable dictionary
        item_data = json.loads(db_project.model_dump_json())  # model_dump_json() handles datetime conversion
        await container.create_item(item_data)
        return db_project
    except CosmosResourceNotFoundError:
        raise HTTPException()
                            

@router.get("/")
async def read_projects(user: User = Depends(get_current_user), db: CosmosClient = Depends(get_db)):
    container = db.get_container_client("projects")
    if user.role == UserRole.ADMIN:
        query = "SELECT * FROM c"
    else:
        query = f"SELECT * FROM c WHERE c.owner_id = '{user.id}'"
    try:
        items = []
        async for item in container.query_items(query=query):
            items.append(Project(**item))
        return items
    except CosmosHttpResponseError as e:
        # logger.error(f"Project query error: {str(e)}")
        raise HTTPException(status_code=400, detail="Error querying projects")

@router.get("/{project_id}")
async def read_project(project_id: str, user: User = Depends(get_current_user), db: CosmosClient = Depends(get_db)):
    try:
        container = db.get_container_client("projects")
        project = await container.read_item(item=project_id, partition_key=user.id)
        project = Project(**project)
        check_project_access(user, project)
        return project
    except CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")
    except CosmosHttpResponseError as e:
        # logger.error(f"Project read error: {str(e)}")
        raise HTTPException(status_code=400, detail="Error reading project")

@router.put("/{project_id}")
async def update_project(project_id: str, project_update: ProjectUpdate, user: User = Depends(get_current_user), db: CosmosClient = Depends(get_db)):
    try:
        container = db.get_container_client("projects")
        project = await container.read_item(item=project_id, partition_key=user.id)
        project = Project(**project)
        # check_project_access(user, project, require_owner=user.role != UserRole.ADMIN)
        check_project_access(user, project, require_owner=True)
        
        update_data = project_update.dict(exclude_unset=True)

        updated_project = Project(
            id=project.id,
            title=update_data.get("title", project.title),
            description=update_data.get("description", project.description),
            status=update_data.get("status", project.status),
            start_date=project.start_date,
            end_date=project.end_date,
            owner_id=project.owner_id,
            updated_at=datetime.utcnow()  # Set updated_at on update
        )
        # Convert to JSON-serializable dictionary
        item_data = json.loads(updated_project.model_dump_json())

        if user.role == UserRole.MEMBER and "status" in update_data:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Members cannot update project status")
        
        for key, value in update_data.items():
            setattr(project, key, value)
        # project.updated_at = datetime.utcnow()
        # await container.replace_item(item=project_id, body=project.dict())
        
        await container.replace_item(item=project_id, body=item_data)
        return project
    except CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")
    except CosmosHttpResponseError as e:
        # logger.error(f"Project update error: {str(e)}")
        raise HTTPException(status_code=400, detail="Error updating project")

@router.delete("/{project_id}")
async def delete_project(project_id: str, user: User = Depends(get_current_user), db: CosmosClient = Depends(get_db)):
    try:
        container = db.get_container_client("projects")
        project = await container.read_item(item=project_id, partition_key=user.id)
        project = Project(**project)
        check_project_access(user, project, require_owner=True)
        await container.delete_item(item=project_id, partition_key=user.id)
        return {"message": "Project deleted successfully"}
    except CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")
    except CosmosHttpResponseError as e:
        # logger.error(f"Project deletion error: {str(e)}")
        raise HTTPException(status_code=400, detail="Error deleting project")