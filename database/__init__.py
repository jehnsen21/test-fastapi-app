# project-management-api/database/__init__.py
from database.cosmos_client import CosmosClientSingleton

async def get_db():
    return await CosmosClientSingleton.get_instance()

__all__ = ['CosmosClientSingleton', 'get_db']