from fastapi import APIRouter, Depends, HTTPException, status
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosHttpResponseError
from models.project_model import Project, ProjectCreate, ProjectUpdate
from models.user_model import User
from models.enums import UserRole
from services.auth_service import AuthService
from datetime import datetime
from uuid import uuid4
import json
from services.project_service import ProjectService 
from models.project_model import ProjectResponse


router = APIRouter(prefix="/projects", tags=["projects"])

project_service = ProjectService()
auth_service = AuthService()

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate, user: User = Depends(auth_service.get_current_user)):
    try:
        return await project_service.create_project(project, user)
    except CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Resource not found")
    except CosmosHttpResponseError as e:
        raise HTTPException(status_code=400, detail=f"Error creating project: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
                            
@router.get("/")
async def read_projects(user: User = Depends(auth_service.get_current_user)):
    try:
        return await project_service.get_projects(user)
    except CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="No projects found")

@router.get("/{project_id}")
async def read_project(project_id: str, user: User = Depends(auth_service.get_current_user)):
    try:
        return await project_service.get_project_by_id(project_id, user.id, user)
    except CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")
  
@router.put("/{project_id}")
async def update_project(project_id: str, project_update: ProjectUpdate, user: User = Depends(auth_service.get_current_user)):
    try:
        return await project_service.update_project(project_id, project_update, user)
    except CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")
    except CosmosHttpResponseError as e:
        # logger.error(f"Project update error: {str(e)}")
        raise HTTPException(status_code=400, detail="Error updating project")

@router.delete("/{project_id}")
async def delete_project(project_id: str, user: User = Depends(auth_service.get_current_user)):
    try:
        result = await project_service.delete_project(project_id, user)
        return result #{"message": "Project deleted successfully"}
    except CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")
    except CosmosHttpResponseError as e:
        # logger.error(f"Project deletion error: {str(e)}")
        raise HTTPException(status_code=400, detail="Error deleting project")