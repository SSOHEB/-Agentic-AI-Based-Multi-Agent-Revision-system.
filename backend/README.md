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
│   ├── core/                        # App-wide infrastructure (config, db, auth, retention)
│   ├── routers/                     # HTTP endpoints (FastAPI routers)
│   ├── models/                      # SQLAlchemy ORM models
│   ├── schemas/                     # Pydantic schemas for request/response validation
│   ├── repositories/                # Data access layer for database queries
│   ├── services/                    # Business logic bridging routers and agents
│   ├── agents/                      # LangGraph AI agents (Scheduler, RAG, Quiz, Eval, Progress)
│   ├── tools/                       # Reusable tools for agents (RAG retriever, DB accessor)
│   ├── tasks/                       # Background workers/cron jobs
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

### 5. Retention Engine (`retention.py`)
Pure-Python module for spaced-repetition mathematics. No database dependency.
* **`compute_topic_retention(performance_score, days_since_session, interval_day)`**: Calculates current retention using a linear decay model, clamped to `[0.10, 1.00]`.
* **`compute_retention_after(prev_retention, session_performance, interval_day)`**: Blends historical retention with new session performance using interval-based weights.
* **`compute_system_retention(topics)`**: Computes weighted aggregate retention across all topics, accounting for topic state (active/decaying/graduated) and interval importance weights. Graduated topics do not decay.

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
* **Fields**: `title`, `description` (nullable), `difficulty_level` (integer).
* **Scheduling Fields**: `current_interval_day` (int, default 1), `next_review_date` (nullable datetime), `state` (string: "active", "decaying", or "graduated").
* **Relationships**: Links back to the `User` owner via `topic.user`.

### `quiz_session.py`
The ORM model representing the `quiz_sessions` table (individual revision test instances).
* Inherits from `Base` and `TimestampMixin`.
* **Primary Key**: `id` (UUID4).
* **Foreign Keys**: 
  * `user_id` mapped strictly to `users.id` (CASCADE deletion).
  * `topic_id` mapped to `topics.id` (CASCADE deletion, **nullable** to support multi-topic sessions via the junction table).
* **Fields**: `started_at` (DateTime), `ended_at` (nullable DateTime), `score` (nullable float), `difficulty_level` (int), and `status` (string: "active", "completed", "pre_generated").
* **Relationships**: Links back to the `User` actor via `quiz_session.user`.

### `session_topic.py`
The junction table model linking quiz sessions to multiple topics.
* **Table**: `session_topics`.
* **Composite Primary Key**: (`session_id`, `topic_id`).
* **Foreign Keys**: `session_id` → `quiz_sessions.id`, `topic_id` → `topics.id` (both CASCADE).
* Enables batch scheduling: one quiz session can cover multiple topics.

### `answer.py`
The ORM model representing the `answers` table (stores individual answers submitted during a quiz session).
* Inherits from `Base` and `TimestampMixin`.
* **Primary Key**: `id` (UUID4).
* **Foreign Key**: `session_id` mapped strictly to `quiz_sessions.id` (CASCADE deletion).
* **Fields**: `question_id` (UUID4) and `answer_text` (string).

### `question.py`
The ORM model representing the `questions` table (the actual questions served during a quiz session).
* Inherits from `Base` and `TimestampMixin`.
* **Primary Key**: `id` (UUID4).
* **Foreign Key**: `quiz_session_id` mapped strictly to `quiz_sessions.id` (CASCADE deletion).
* **Fields**: `question_text`, `question_type`, `difficulty`, `options` (JSON), and `correct_answer`.

### `performance_log.py`
The ORM model representing the `performance_log` table, which tracks a student's accuracy and historical progress.
* Inherits from `Base`.
* **Primary Key**: `id` (UUID4).
* **Foreign Keys**: `user_id`, `topic_id`, and `session_id` to establish full relational tracking.
* **Fields**: `performance_score` (float), `retention_before` (float), `retention_after` (float), and `logged_at` (datetime).

## Validation Schemas (`backend/schemas/`)
This directory contains Pydantic v2 models used to validate incoming request data and format outgoing response data.

### `user_schema.py`
Defines the Pydantic schemas for User-related operations.
* **`UserCreate`**: Validates payload when a new user registers (`email`, `name`, `firebase_uid`).
* **`UserResponse`**: Formats the secure outgoing representation of a user. It uses `model_config = ConfigDict(from_attributes=True)` to easily convert SQLAlchemy User ORM models directly into JSON containing `id`, `email`, `name`, and `is_active`.

### `answer_schema.py`
Defines the Pydantic schemas for Answer-related operations.
* **`AnswerSubmitRequest`**: Validates payload when a user submits an answer to a quiz question (`session_id`, `question_id`, `answer_text`).
* **`AnswerResponse`**: Formats the outgoing response of a submitted answer, converting the SQLAlchemy ORM model into JSON.

### `question_schema.py`
Defines the Pydantic schemas for Question-related operations.
* **`QuestionResponse`**: Formats the outgoing JSON representation of a quiz question, containing the ID, text, type, difficulty, and MCQ options list.

### `performance_schema.py`
Defines the Pydantic schemas for Performance Tracking.
* **`PerformanceLogResponse`**: Formats the outgoing JSON representation of a calculated performance log, including exactly how well a user performed on a specific session and their retention metrics.

### `session_schema.py`
Defines the Pydantic schema for the session completion endpoint.
* **`SessionCompleteResponse`**: Returns `session_id` and `status` after a quiz session is finalized.

### `progress_schema.py`
Defines the Pydantic schema for the progress dashboard.
* **`DashboardResponse`**: Returns `retention_percent`, `trend`, `exam_readiness`, `topics_total`, and `topics_graduated`.

### `scheduler_schema.py`
Defines the Pydantic schema for the scheduler.
* **`SchedulerResponse`**: Returns `session_id` (nullable), `topics_count`, and `status` ("created" or "no_topics_due").

### `question_generation_schema.py`
Defines the Pydantic schema for question generation.
* **`QuestionGenerationResponse`**: Returns `session_id` and `questions_created` count.

## Data Access Layer (`backend/repositories/`)
This directory contains repository classes that abstract away direct database queries using SQLAlchemy.

### `user_repository.py`
Provides database access methods for the User entity via the `UserRepository` class.
* Uses `AsyncSession` to safely query the database.
* Includes methods to `create` new users, and fetch them via `get_by_email` and `get_by_id`.

### `answer_repository.py`
Provides database access for the Answer entity.
* Handles saving new answers and retrieving a list of answers for a specific quiz session via `get_session_answers`.

### `question_repository.py`
Provides database access for the Question entity.
* Retrieves all questions mapped to a specific quiz session ID via `get_questions_by_session`.

### `performance_repository.py`
Provides database access for the PerformanceLog entity.
* Creates new tracking entries securely in the database (`create_log`).
* Queries the chronologically most recent performance metric for a given user's scope (`get_latest_topic_performance`).

### `session_repository.py`
Provides database access for the QuizSession entity.
* Creates new quiz sessions (`create`), fetches them (`get_session`), and safely updates their status (`update_session_status` with None guard).

### `progress_repository.py`
Provides read-only database access for progress analytics.
* Fetches user topics, recent performance logs, graduated topic counts, and the latest performance log per topic.

### `scheduler_repository.py`
Provides database access for the scheduler engine.
* **`get_due_topics(user_id)`**: Queries topics where `next_review_date <= NOW()` (excluding graduated topics).
* **`create_quiz_session(user_id)`**: Creates a pre-generated quiz session.
* **`attach_topics_to_session(session_id, topic_ids)`**: Links topics to a session via the `session_topics` junction table.

### `question_generation_repository.py`
Provides database access for question generation.
* **`get_session_topics(session_id)`**: Fetches topics linked to a session via the `session_topics` junction table.
* **`create_questions(session_id, questions)`**: Bulk-inserts generated questions for a session.

## Business Logic Layer (`backend/services/`)
This directory contains service classes that handle core application and business rules, acting as the middleman between Routers and Repositories.

### `user_service.py`
Contains the `UserService` class.
* Takes a `UserRepository` instance to perform data operations.
* Contains the `create_user` complex logic: checks if a user already exists by email, early-returns them if they do, or constructs and saves a new `User` model if they don't.

### `answer_service.py`
Contains the `AnswerService` class.
* Implements logic to construct the SQLAlchemy `Answer` model from incoming validated payloads and handles storing it via the repository.

### `performance_service.py`
Contains the `PerformanceService` class.
* Extracts historical answer metrics dynamically and calculates floating-point accuracy metrics linking quiz models. Includes future-proof hooks for invoking retention formulas.

### `session_service.py`
Contains the `SessionService` class.
* Orchestrates the session completion pipeline: validates the session exists, prevents double completion, logs performance via `PerformanceService`, and marks the session as completed.
* Dependencies: `SessionRepository` and `PerformanceService` only (clean DI).

### `progress_service.py`
Contains the `ProgressService` class.
* Builds the full progress dashboard for a user: fetches topics/performance data, calls `compute_system_retention` from `core.retention`, calculates exam readiness (`coverage * 0.50 + avg_l3_score * 0.30 + retention * 0.20`), and returns `DashboardResponse`.

### `scheduler_service.py`
Contains the `SchedulerService` class.
* Orchestrates quiz session generation: fetches due topics, caps at 5, creates one session, attaches topics via the junction table, and returns a summary.

### `question_generation_service.py`
Contains the `QuestionGenerationService` class.
* Generates placeholder MCQ questions (2 per topic, L1/L2 difficulty) for a scheduled session. Will later integrate with RAG retrieval and the Quiz Agent for AI-based question generation.

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

#### `topic_router.py`
Defines the Topic-related endpoints (`POST /topics/` and `GET /topics/user/{user_id}`).
* Injects the `AsyncSession` database dependency.
* Instantiates the `TopicRepository` and `TopicService`.
* Handles the creation of new topics and fetching existing topics for a specific user.

#### `answer_router.py`
Defines the Answer-related endpoints (`POST /quiz/answer`).
* Injects the `AsyncSession` database dependency.
* Instantiates the `AnswerRepository` and `AnswerService` to persist student responses.

#### `quiz_router.py`
Defines Quiz Session-related endpoints (`POST /quiz/start` and `GET /quiz/{session_id}/questions`).
* Injects `AsyncSession` dependency.
* Initiates new quiz sessions, and fetches the list of generated questions for an active session to surface to the frontend.

#### `sessions.py`
Defines the session completion endpoint (`POST /sessions/{session_id}/complete`).
* Instantiates `SessionRepository` and `PerformanceService`, passes them to `SessionService`.
* Finalizes a quiz session: logs performance and marks it as completed.

#### `progress.py`
Defines the progress dashboard endpoint (`GET /progress/dashboard?user_id=`).
* Returns learning analytics: retention percent, trend, exam readiness, topic counts.
* Uses `core.retention` for all retention math.

#### `scheduler.py`
Defines the scheduler endpoint (`POST /scheduler/generate?user_id=`).
* Generates pre-built quiz sessions for topics that are due for review.
* Creates one session and attaches up to 5 topics via the junction table.

#### `question_generation.py`
Defines the question generation endpoint (`POST /quiz/{session_id}/generate`).
* Generates placeholder MCQ questions for all topics attached to a session.
* Returns the count of questions created.

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
* Exposes `Base.metadata` to securely detect all models (`users`, `topics`, `quiz_sessions`, `session_topics`, `questions`, `answers`, `performance_log`) for the `python -m alembic revision --autogenerate` command.
* **Latest migration** (`f3a1b2c4d5e6`): Adds scheduling columns to `topics` (`current_interval_day`, `next_review_date`, `state`), creates the `session_topics` junction table, and makes `quiz_sessions.topic_id` nullable.
* To apply generated migrations to your database, simply run `python -m alembic upgrade head` from within the `backend` directory.

### 9. Tests (`tests/`)
Contains all automated verification checks.
* **`test_health.py`**: An asynchronous test using `pytest` and `httpx` to ping the root endpoint and assert it successfully returns `{status: ok}`.
* **`test_retention.py`**: Smoke tests for the `core/retention.py` module verifying decay clamping, rounding, weighted averages, graduated topic stability, decaying state multiplier, and mixed-topic scenarios.

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


