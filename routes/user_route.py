# from fastapi import FastAPI, Depends
# from pydantic import BaseModel
# from azure.cosmos import CosmosClient
# from services.cosmos_service import CosmosService
# from typing import List

# app = FastAPI()

# # # Example Pydantic model
# # class User(BaseModel):
# #     id: str
# #     name: str
# #     email: str

# # Dependency injection for Cosmos DB client
# def get_cosmos_client():
#     client = CosmosClient(
#         url="your_cosmos_db_url",
#         credential="your_cosmos_db_key"
#     )
#     return client

# # Create service instance
# def get_user_service(client: CosmosClient = Depends(get_cosmos_client)):
#     return CosmosService[User](
#         client=client,
#         database_name="your_database",
#         container_name="users",
#         partition_key_path="/id"
#     )

# # API endpoints
# @app.post("/users/", response_model=User)
# async def create_user(user: User, service: CosmosService[User] = Depends(get_user_service)):
#     return await service.create(user)

# @app.get("/users/{user_id}", response_model=User)
# async def get_user(user_id: str, partition_key: str, service: CosmosService[User] = Depends(get_user_service)):
#     return await service.read(user_id, partition_key)

# @app.get("/users/", response_model=List[User])
# async def get_all_users(partition_key: str = None, service: CosmosService[User] = Depends(get_user_service)):
#     return await service.read_all(partition_key)

# @app.put("/users/{user_id}", response_model=User)
# async def update_user(user_id: str, partition_key: str, user: User, service: CosmosService[User] = Depends(get_user_service)):
#     return await service.update(user_id, partition_key, user)

# @app.delete("/users/{user_id}")
# async def delete_user(user_id: str, partition_key: str, service: CosmosService[User] = Depends(get_user_service)):
#     await service.delete(user_id, partition_key)
#     return {"message": "User deleted successfully"}