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
