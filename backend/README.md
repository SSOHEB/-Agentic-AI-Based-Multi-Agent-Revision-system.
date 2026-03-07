# Backend Documentation

This document provides an overview of the backend architecture, folder structure, and the core modules implemented so far.

## Tech Stack
* **Python**: 3.11
* **Framework**: FastAPI
* **Database**: PostgreSQL (Neon) with SQLAlchemy 2.0 (asyncio) and pgvector
* **Authentication**: Firebase Admin SDK (JWT)
* **Configuration**: pydantic-settings
* **AI/LLM**: Google Gemini Flash
* **Agent Orchestration**: LangGraph

## Folder Structure

```text
backend/
│   ├── main.py                      # App entry point
│   ├── requirements.txt
│   ├── .env
│   ├── .env.example                 # Template for environment variables
│   │
│   ├── core/                        # App-wide infrastructure (config, db, auth)
│   ├── routers/                     # HTTP endpoints (FastAPI routers)
│   ├── models/                      # SQLAlchemy ORM models
│   ├── schemas/                     # Pydantic schemas for request/response validation
│   ├── repositories/                # Data access layer for database queries
│   ├── services/                    # Business logic bridging routers and agents
│   ├── agents/                      # LangGraph AI agents (Scheduler, RAG, Quiz, Eval, Progress)
│   ├── tools/                       # Reusable tools for agents (RAG retriever, DB accessor)
│   ├── tasks/                       # Background background workers/cron jobs
│   ├── memory/                      # LangGraph checkpoint persistence
│   ├── tests/                       # Unit and integration tests
│   └── migrations/                  # Alembic database migrations
```

## Core Modules (`backend/core/`)

The `core` directory contains the foundational infrastructure required to run the application. Every other folder imports from here.

### 1. Configuration (`config.py`)
Centralized configuration management using `pydantic-settings`.
* Loads environment variables from a `.env` file.
* Provides strongly-typed configuration fields for:
  * `ENVIRONMENT` (development, staging, production)
  * `DATABASE_URL`
  * `SECRET_KEY`
  * `GEMINI_API_KEY`
  * `RESEND_API_KEY`
  * `FIREBASE_CREDENTIALS_PATH`
* Exports a singleton `settings` object used throughout the app.

### 2. Database (`database.py`)
Manages the asynchronous SQLAlchemy database connection pool and session factory.
* Initializes an `AsyncEngine` connected to PostgreSQL via asyncpg.
* Configures connection pooling (`pool_size=10`, `max_overflow=20`).
* Provides a `get_db()` async generator dependency for FastAPI to inject database sessions into routers.

### 3. Authentication & Firebase (`firebase.py`)
Handles Firebase Admin SDK initialization and token verification.
* Implements a singleton initialization pattern (`init_firebase()`) intended to run during the FastAPI lifespan startup.
* Provides `verify_firebase_token(token)` to validate JWTs provided by clients.

### 4. Dependencies (`dependencies.py`)
Reusable FastAPI dependency injections.
* **`get_db`**: Injects an active `AsyncSession` into route handlers.
* **`get_current_user`**: Secures endpoints by extracting the Bearer token, verifying it against Firebase, and returning the authenticated user's payload. Raises a `401 Unauthorized` exception if the token is invalid or missing.

## Database Models (`backend/models/`)
This directory contains the SQLAlchemy 2.0 ORM classes that define the structure of our PostgreSQL tables.

### `base.py`
The foundation for all database models.
* Defines the primary `Base` class inherited from `DeclarativeBase` that all subsequent models extend.
* Provides a `TimestampMixin` utility class that automatically adds and manages timezone-aware `created_at` and `updated_at` columns on any model it is applied to.

### `user.py`
The ORM model representing the `users` table.
* Inherits from `Base` and `TimestampMixin`.
* **Primary Key**: `id` (UUID4).
* **Fields**: `email` (indexed, unique), `name`, `firebase_uid` (unique constraint for auth linking), and `is_active` (boolean).
* **Relationships**: Contains a `One-to-Many` relationship with `topics` allowing `user.topics` collection access.

### `topic.py`
The ORM model representing the `topics` table (the actual study subjects).
* Inherits from `Base` and `TimestampMixin`.
* **Primary Key**: `id` (UUID4).
* **Foreign Key**: `user_id` mapped strictly to `users.id` causing `CASCADE` deletion if the parent user is deleted.
* **Fields**: `title`, `description` (nullable), and `difficulty_level` (integer).
* **Relationships**: Links back to the `User` owner via `topic.user`.

### `quiz_session.py`
The ORM model representing the `quiz_sessions` table (individual revision test instances).
* Inherits from `Base` and `TimestampMixin`.
* **Primary Key**: `id` (UUID4).
* **Foreign Key**: `user_id` mapped strictly to `users.id` (CASCADE deletion).
* **Fields**: `started_at` (DateTime), `ended_at` (nullable DateTime), `score` (nullable float), `difficulty_level` (int), and `status` (string).
* **Relationships**: Links back to the `User` actor via `quiz_session.user`.

## Validation Schemas (`backend/schemas/`)
This directory contains Pydantic v2 models used to validate incoming request data and format outgoing response data.

### `user_schema.py`
Defines the Pydantic schemas for User-related operations.
* **`UserCreate`**: Validates payload when a new user registers (`email`, `name`, `firebase_uid`).
* **`UserResponse`**: Formats the secure outgoing representation of a user. It uses `model_config = ConfigDict(from_attributes=True)` to easily convert SQLAlchemy User ORM models directly into JSON containing `id`, `email`, `name`, and `is_active`.

## Data Access Layer (`backend/repositories/`)
This directory contains repository classes that abstract away direct database queries using SQLAlchemy.

### `user_repository.py`
Provides database access methods for the User entity via the `UserRepository` class.
* Uses `AsyncSession` to safely query the database.
* Includes methods to `create` new users, and fetch them via `get_by_email` and `get_by_id`.

## Business Logic Layer (`backend/services/`)
This directory contains service classes that handle core application and business rules, acting as the middleman between Routers and Repositories.

### `user_service.py`
Contains the `UserService` class.
* Takes a `UserRepository` instance to perform data operations.
* Contains the `create_user` complex logic: checks if a user already exists by email, early-returns them if they do, or constructs and saves a new `User` model if they don't.

### 5. Application Entrypoint (`main.py`)
The root file that ties the entire backend together.
* Initializes the FastAPI application and registers the lifespan handler (for Firebase startup).
* Configures CORS middleware to allow requests from the frontend.
* Registers all the individual routers (e.g., `/auth`, `/users`, `/topics`) so the API can handle those incoming URLs.
* Provides a root Health Check endpoint (`GET /`) to verify the API is online.

### 6. API Endpoints (`backend/routers/`)
This directory contains the FastAPI routers that define the URLs the frontend can communicate with.

#### `user_router.py`
Defines the `POST /users/` API endpoint.
* Injects the `AsyncSession` database dependency.
* Instantiates the `UserRepository` and `UserService`.
* Passes the incoming `UserCreate` JSON body directly to the service layer and returns a validated `UserResponse`.

### 6. Environment Templates & Requirements
* **`.env.example`**: A documented list of all required environment variables without actual values (safe for version control).
* **`requirements.txt`**: A clean, explicitly versioned list of all python package dependencies to avoid future update conflicts.

### 7. Tests (`tests/`)
Contains all automated verification checks.
* **`test_health.py`**: An asynchronous test using `pytest` and `httpx` to ping the root endpoint and assert it successfully returns `{status: ok}`.

### 8. Database Migrations (`migrations/`)
Alembic is configured to automatically track changes in the SQLAlchemy models and generate versioned migration scripts.
* Employs the `async` template to officially support our async `asyncpg` database connection.
* Dynamically loads `DATABASE_URL` via the runtime `.env` integration inside `env.py`.
* Exposes `Base.metadata` to securely detect the `users`, `topics`, and `quiz_sessions` tables for the `alembic revision --autogenerate` command.

## 9. Backend Fundamentals & Standards

### API Standard Conventions (RESTful)
The backend routes strictly adhere to RESTful methodologies using standard HTTP verbs:
* **`GET`**: Retrieve resources (used for fetching profiles, viewing topics, etc.)
* **`POST`**: Create new resources (used for initializing sessions or adding new topics)
* **`PATCH`**: Partially update resources (used for modifying user settings)
* **`DELETE`**: Remove resources

### HTTP Status Codes
Endpoints return industry-standard HTTP Status Codes indicating request success or failure reasons:
* **`200 OK`**: Successful request execution
* **`201 Created`**: Successful resource creation
* **`400 Bad Request`**: Client-side validation failure / invalid inputs
* **`401 Unauthorized`**: Authentication failure (missing or invalid Firebase token)
* **`404 Not Found`**: Resource does not exist
* **`500 Internal Server Error`**: Unexpected server-side failure

### Database Connectivity
We utilize **SQLAlchemy 2.0** integrated with the **asyncpg** driver to allow for fully non-blocking database queries. 
* By structuring our database connection via `create_async_engine`, FastAPI can fulfill thousands of other incoming HTTP requests simultaneously while awaiting complex Database queries in the background. 
* To prevent connection pooling issues, each HTTP request is injected with an ephemeral database dependency (`AsyncSession`) via `get_db()` which is gracefully torn down and released back into the pool upon request completion.


