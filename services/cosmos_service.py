# project-management-api/services/base_service.py
from typing import Generic, TypeVar, Type, Optional
from azure.cosmos.database import DatabaseProxy
from azure.cosmos.container import ContainerProxy
from azure.cosmos.exceptions import CosmosResourceNotFoundError, CosmosHttpResponseError
from fastapi import HTTPException, status
from database import CosmosClientSingleton
import logging
import json

logger = logging.getLogger(__name__)

T = TypeVar("T")

class CosmosService(Generic[T]):
    def __init__(self, entity_type: Type[T], container_name: str, partition_key_path: str):
        self.entity_type = entity_type
        self._container_name = container_name
        self._partition_key_path = partition_key_path
        self._db = None

    async def _get_database(self) -> DatabaseProxy:
        if self._db is None:
            self._db = await CosmosClientSingleton.get_instance()
        return self._db

    async def get_container(self) -> ContainerProxy:
        database = await self._get_database()
        return database.get_container_client(self._container_name)

    async def create(self, entity: T) -> T:
        entity = await self.pre_create(entity)
        try:
            container = await self.get_container()
            item_data = json.loads(entity.model_dump_json())
            await container.create_item(item_data)
            entity = await self.post_create(entity)
            return entity
        except CosmosHttpResponseError as e:
            logger.error(f"Error creating {self._container_name}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error creating {self._container_name}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error creating {self._container_name}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}")

    async def read(self, item_id: str, partition_key_value: str) -> Optional[T]:
        try:
            container = await self.get_container()
            item = await container.read_item(item=item_id, partition_key=partition_key_value)
            return self.entity_type(**item)
        except CosmosResourceNotFoundError:
            logger.error(f"{self._container_name} {item_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{self._container_name} {item_id} not found")
        except CosmosHttpResponseError as e:
            logger.error(f"Error reading {self._container_name}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error reading {self._container_name}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error reading {self._container_name}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}")

    async def update(self, item_id: str, entity: T, partition_key_value: str) -> T:
        try:
            container = await self.get_container()
            item_data = json.loads(entity.model_dump_json())
            await container.replace_item(item=item_id, body=item_data)
            return entity
        except CosmosResourceNotFoundError:
            logger.error(f"{self._container_name} {item_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{self._container_name} {item_id} not found")
        except CosmosHttpResponseError as e:
            logger.error(f"Error updating {self._container_name}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error updating {self._container_name}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error updating {self._container_name}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}")

    async def delete(self, item_id: str, partition_key_value: str) -> None:
        try:
            container = await self.get_container()
            await container.delete_item(item=item_id, partition_key=partition_key_value)
        except CosmosResourceNotFoundError:
            logger.error(f"{self._container_name} {item_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{self._container_name} {item_id} not found")
        except CosmosHttpResponseError as e:
            logger.error(f"Error deleting {self._container_name}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error deleting {self._container_name}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error deleting {self._container_name}: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}") 

    async def pre_create(self, entity: T) -> T:
        """Hook for pre-create logic."""
        return entity

    async def post_create(self, entity: T) -> T:
        """Hook for post-create logic."""
        return entity