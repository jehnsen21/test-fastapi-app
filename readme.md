## Backend Service built in FastAPI

# Entities:
- User
- Project

# Database
- Azure CosmosDB

project-management-api/
│
├── app/                    # Main application package
│   ├── __init__.py         # Marks app as a package
│   ├── main.py            # Entry point of the FastAPI application
│   ├── config.py          # Configuration settings (e.g., environment variables)
│   ├── dependencies.py    # Dependency injection setup (e.g., get_db, get_current_user)
│   ├── exceptions.py      # Custom exception handlers
│   └── middleware.py      # Custom middleware (e.g., logging, authentication)
│
├── routers/                # API route definitions
│   ├── __init__.py         # Marks routers as a package
│   ├── auth.py            # Authentication routes (/auth)
│   ├── projects.py        # Project management routes (/projects)
│   ├── users.py           # User management routes (/users)
│   └── v1/                # Versioned API routes (optional for future scalability)
│       ├── __init__.py
│       ├── auth.py
│       ├── projects.py
│       └── users.py
│
├── models/                 # Pydantic models and schemas
│   ├── __init__.py         # Marks models as a package
│   ├── base.py            # Base model configurations
│   ├── user.py            # User-related models (User, UserCreate)
│   ├── project.py         # Project-related models (Project, ProjectCreate, ProjectUpdate)
│   └── enums.py           # Enums (e.g., ProjectStatus, UserRole)
│
├── database/               # Database-related code
│   ├── __init__.py         # Marks database as a package
│   ├── client.py          # Cosmos DB client singleton and configuration
│   ├── init_db.py         # Database initialization logic
│   └── migrations/        # Database migration scripts (if needed)
│
├── services/               # Business logic and services
│   ├── __init__.py         # Marks services as a package
│   ├── auth_service.py    # Authentication logic (e.g., password hashing, JWT)
│   ├── project_service.py # Project-related business logic
│   └── user_service.py    # User-related business logic
│
├── tests/                  # Unit and integration tests
│   ├── __init__.py         # Marks tests as a package
│   ├── conftest.py        # pytest fixtures (e.g., test client, mock DB)
│   ├── unit/              # Unit tests
│   │   ├── test_auth.py
│   │   ├── test_projects.py
│   │   └── test_users.py
│   ├── integration/       # Integration tests
│   │   ├── test_auth.py
│   │   ├── test_projects.py
│   │   └── test_users.py
│   └── data/              # Test data (e.g., JSON fixtures)
│
├── scripts/                # Utility scripts
│   ├── __init__.py         # Marks scripts as a package
│   ├── seed_data.py       # Script to seed initial data
│   └── migrate_data.py    # Data migration script
│
├── docs/                   # API documentation
│   ├── __init__.py         # Marks docs as a package
│   ├── openapi.json       # Generated OpenAPI schema
│   └── README.md          # Documentation overview
│
├── static/                 # Static files (if needed, e.g., for Swagger UI customization)
│
├── .env                    # Environment variables (e.g., COSMOS_ENDPOINT, SECRET_KEY)
├── .gitignore              # Git ignore file
├── pyproject.toml          # Project metadata and dependencies (e.g., poetry)
├── README.md               # Project overview and setup instructions
├── requirements.txt        # Dependency list (if not using poetry)
├── Dockerfile             # Docker configuration for deployment
├── docker-compose.yml     # Docker Compose for local development
└── Makefile               # Optional: Automation scripts (e.g., run, test, lint)