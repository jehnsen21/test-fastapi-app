# project-management-api/services/project_service.py
from fastapi import HTTPException, Depends, status
from models.user_model import User
from models.project_model import Project, ProjectCreate, ProjectUpdate, ProjectResponse
from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosHttpResponseError
# from models.schemas import schemas as schemas
from models.enums import UserRole, ProjectStatus
from services.cosmos_service import CosmosService
from services.auth_service import AuthService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ProjectService(CosmosService[Project]):
    def __init__(self):
        super().__init__(Project, container_name="projects", partition_key_path="/owner_id")

    async def create_project(self, project: ProjectCreate, user: User) -> ProjectResponse:
        if user.role == UserRole.MEMBER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Members cannot create projects")
        
        db_project = Project(
            title=project.title,
            description=project.description,
            status=project.status or ProjectStatus.PENDING,
            start_date=project.start_date or datetime.utcnow(),
            end_date=project.end_date or datetime.utcnow(),
            owner_id=user.id,
            updated_at=datetime.utcnow()
        )
        # print("DB_PROJECT", db_project)
        return  await self.create(db_project)
        # return ProjectResponse(**created_project.model_dump())

    async def update_project(self, project_id: str, project_update: ProjectUpdate, user: User) -> ProjectResponse:
        existing_project = await self.read(project_id, user.id)
        if existing_project.owner_id != user.id and user.role != UserRole.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not project owner")

        updated_project = Project(
            id=project_id,
            title=project_update.title or existing_project.title,
            description=project_update.description or existing_project.description,
            status=project_update.status or existing_project.status,
            start_date=existing_project.start_date,
            end_date=project_update.end_date or existing_project.end_date,
            owner_id=existing_project.owner_id,
            updated_at=datetime.utcnow()
        )
        updated_project = await self.update(project_id, updated_project, user.id)
        return ProjectResponse(**updated_project.model_dump())
    
    async def get_projects(self,  user: User):
        print("USER ", user)
        container = await self.get_container()
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
            logger.error(f"Project query error: {str(e)}")
        raise HTTPException(status_code=400, detail="Error querying projects")
    
    async def get_project_by_id(self, project_id: str, partition_key: str, user: User):
        
        try:
            project = await self.read(project_id, partition_key)
            print("project:", project)
            return project
        except CosmosResourceNotFoundError:
            raise HTTPException(status_code=404, detail="Project not found")
        except CosmosHttpResponseError as e:
            # logger.error(f"Project read error: {str(e)}")
            raise HTTPException(status_code=400, detail="Error reading project")
    
    async def delete_project(self, project_id, user):
        project = self.read(project_id, user.id)
        if project is None:
            raise CosmosResourceNotFoundError(status_code=404, detail="Project doesn't exist")
        # self.check_project_access(True)
        return await self.delete(project_id, user.id) 