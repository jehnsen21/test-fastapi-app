from azure.cosmos import PartitionKey, exceptions
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
        return cls._instance

    async def get_database_client(self, db_name):
        if self._database is None:
            self._database = await self._client.create_database_if_not_exists(id=db_name)
        return self._database

    async def get_database(self):
        client = CosmosClientSingleton()
        database = await client.get_database_client(settings.DATABASE_NAME)
        return database

    async def close(self):
        if self._client:
            await self._client.close()

async def init_db():
    try:
        client = CosmosClientSingleton()
        database = await client.get_database_client(settings.DATABASE_NAME)
        
        # Create users container
        await database.create_container_if_not_exists(
            id="users",
            partition_key=PartitionKey(path="/username"), 
            offer_throughput=400
        )
        
        # Create projects container (fixed partition key)
        await database.create_container_if_not_exists(
            id="projects",
            partition_key=PartitionKey(path="/owner_id"), 
            offer_throughput=400
        )
        logger.info("Database initialized successfully")
    except exceptions.CosmosHttpResponseError as e: 
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

async def get_db():
    """Dependency to get database client"""
    try:
        client = CosmosClientSingleton()
        database = await client.get_database()
        return database
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise