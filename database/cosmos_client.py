# database/cosmos_client.py
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from config import settings
import logging

logger = logging.getLogger(__name__)

class CosmosClientSingleton:
    _instance = None
    _client = None
    _database = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._client = AsyncCosmosClient(settings.COSMOS_ENDPOINT, credential=settings.COSMOS_KEY)
            logger.info(f"Cosmos DB client initialized at {settings.COSMOS_ENDPOINT} on 2025-06-05 13:01:00 PST")
        return cls._instance

    async def get_database_client(self, db_name):
        if self._database is None:
            self._database = await self._client.create_database_if_not_exists(id=db_name)
        return self._database

    @staticmethod
    async def get_instance():
        client = CosmosClientSingleton()
        database = await client.get_database_client(settings.DATABASE_NAME)
        return database

    async def close(self):
        if self._client:
            await self._client.close()
            logger.info("Cosmos DB client connection closed")
            self._client = None
            self._database = None