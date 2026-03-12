# Python & FastAPI Complete Beginner's Walkthrough

Welcome! If you're new to Python or the FastAPI framework, you might feel a bit overwhelmed looking at the codebase. This guide takes you on a bottom-to-top journey through how our backend is built, explaining the syntax, the architecture, and how exactly a feature (like creating a "Topic") goes from the database all the way to the user's browser.

---

## 1. Python Syntax Crash Course (For This Project)

Before diving into the architecture, here are the Python concepts you'll see everywhere in this project:

### Imports
At the top of every file, you'll see `import` statements. This is simply Python's way of bringing tools from other files into the current file so you can use them.
```python
# Import a tool built into Python itself
import uuid 

# Import a specific class from a third-party library we installed
from fastapi import APIRouter 

# Import something from our own project folder (backend -> models -> user.py)
from backend.models.user import User  
```

### Type Hinting
Python is naturally "dynamically typed" (it guesses if a variable is text or a number). However, in modern projects, we use **Type Hinting** to explicitly tell ourselves (and our code editors) what type of data to expect. This prevents bugs!
```python
# The ": str" tells us "name" must be a string (text).
# The "-> int" tells us this function will return an integer (number).
def calculate_age(name: str, birth_year: int) -> int:
    return 2026 - birth_year
```

### Async and Await
Our backend is extremely fast because it uses **Asynchronous** programming.
Normally, if Python asks the database a question, it stops and waits (freezing the whole app) until the database answers. 
Instead, we use `async def` to create functions that can "pause" their work using the `await` keyword. While they wait for the database, FastAPI goes and serves other users!
```python
# By adding "async", we tell Python this function can pause.
async def get_user_data(user_id: str):
    # The "await" tells Python: "Pause this function until the database answers. Go do something else in the meantime!"
    data = await database.fetch(user_id) 
    return data
```

### Object-Oriented Programming (Classes)
We use `class` blueprints to bundle related data and functions together. We use this heavily for things like *Services* and *Repositories*.
```python
# This is a blueprint
class Calculator:
    def __init__(self, starting_number: int):
        # This function runs automatically when someone creates a Calculator
        self.total = starting_number
        
    def add(self, amount: int):
        # "self" just means "this specific calculator's data"
        self.total += amount

# We "instantiate" an actual calculator object based on the blueprint
my_calc = Calculator(10)
my_calc.add(5) # Total is now 15
```

---

## 2. Our Layered Architecture: Bottom to Top

To keep our code organized and bug-free, we separate it into strict "Layers". Data flows up through the layers when a user requests it, and flows down when a user saves it. Let's trace how the `Topics` feature is built, starting from the lowest level (the Database) to the highest level (the Router URL).

### Layer 1: The Database Model (`backend/models/topic.py`)
At the very bottom, we need to tell PostgreSQL what our table looks like. We use a library called **SQLAlchemy**. This library lets us write a Python Class, and it magically translates it into SQL database tables.

```python
# We import special tools from SQLAlchemy
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from backend.models.base import Base # Our custom letterhead

class Topic(Base):
    __tablename__ = "topics" # The actual name of the table in PostgreSQL

    # We define the columns the database should expect
    # "Mapped[str]" is the type hint. "mapped_column" tells SQLAlchemy how to build the Excel-like spreadsheet column.
    title: Mapped[str] = mapped_column(String, nullable=False)
    difficulty_level: Mapped[int] = mapped_column(Integer, default=1)
    
    # We can also define Foreign Keys to link tables together! (e.g. linking to a User or a Topic)
    # user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
```
*Note: As our project grew, we added models like `QuizSession`, `Question`, `Answer`, and `PerformanceLog` which heavily use ForeignKeys to securely link a student's answer sheet or final report card directly back to their dynamically generated test session!*

*To physically create or update these tables in the PostgreSQL database after writing the Python model classes, we use **Alembic**. Running `python -m alembic revision --autogenerate -m "message"` generates a script for the changes, and `python -m alembic upgrade head` safely applies those changes to the live database.*

### Layer 2: The Validation Schemas (`backend/schemas/topic_schema.py`)
Now that the database exists, we need to protect it. Users are clumsy. If they try to create a "Topic", they might forget to send a `title`, or they might send a `difficulty_level` of "banana". 

We use **Pydantic** to build "Schemas". Schemas act like bouncers at a club. They look at the incoming JSON data from the browser and reject it if it doesn't match the rules.

```python
from pydantic import BaseModel
from typing import Optional

# This validates INCCOMING data (when the user wants to create a topic)
class TopicCreate(BaseModel):
    title: str # Must be provided!
    description: Optional[str] = None # Optional, can be empty
    difficulty_level: Optional[int] = None 
    user_id: str

# This formats OUTGOING data (when we send the info back to the user)
class TopicResponse(BaseModel):
    id: str
    title: str
    # ...
```

### Layer 3: The Repository Layer (`backend/repositories/topic_repository.py`)
We never let our main application talk to the database directly. It's too messy! Instead, we create a "Repository". The Repository is the *only* file allowed to talk to the database about Topics. 

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.topic import Topic

class TopicRepository:
    # When initialized, it requires an active Database Session connection
    def __init__(self, session: AsyncSession):
        self.session = session

    # It provides simple functions we can re-use anywhere
    async def get_user_topics(self, user_id: str):
        # We build an SQL query: "SELECT * FROM topics WHERE topics.user_id = user_id"
        stmt = select(Topic).where(Topic.user_id == user_id)
        # We await the database to execute it!
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
```

### Layer 4: The Service Layer (`backend/services/topic_service.py`)
The Service Layer contains the "Business Logic". This is where we do math, format strings, make decisions, or enforce company rules before we save things. The Service uses the Repository to actually save the work.

```python
from backend.models.topic import Topic
from backend.repositories.topic_repository import TopicRepository
from backend.schemas.topic_schema import TopicCreate

class TopicService:
    # The service expects a repository so it knows how to save things
    def __init__(self, repository: TopicRepository):
        self.repository = repository

    async def create_topic(self, data: TopicCreate) -> Topic:
        # BUSINESS LOGIC: If the user didn't specify a difficulty, default to 1!
        difficulty = data.difficulty_level if data.difficulty_level is not None else 1
        
        # We build the actual SQLAlchemy Database model instance
        new_topic = Topic(
            title=data.title,
            description=data.description,
            difficulty_level=difficulty,
            user_id=data.user_id
        )
        
        # We hand it off to the Repository to safely store it
        return await self.repository.create(new_topic)
```

### Layer 5: The FastAPI Router (`backend/routers/topic_router.py`)
This is the very top layer. This is the API endpoint the Frontend (React site) actually talks to over the internet.

We use **Decorators** (the `@` symbol) to attach a URL to a function.

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.core.dependencies import get_db

# We create a new "Waiter" for the /topics URL
router = APIRouter(prefix="/topics")

# The decorator tells FastAPI: "If someone sends a POST request to /topics, run this function!"
# response_model tells FastAPI to automatically use our Pydantic Bouncer to format the output.
@router.post("/", response_model=TopicResponse)
async def create_topic(
    topic_data: TopicCreate, # FastAPI automatically parses the incoming JSON into our Pydantic Schema!
    db: AsyncSession = Depends(get_db) # FastAPI automatically injects an active Database connection!
):
    # 1. We create the Repository, handing it the DB connection
    repository = TopicRepository(db)
    
    # 2. We create the Service, handing it the Repository
    service = TopicService(repository)
    
    # 3. We tell the Service to execute the business logic!
    return await service.create_topic(topic_data)
```

### Layer 6: Connecting it in Main (`backend/main.py`)
Finally, we have to tell our main FastAPI application that the new Topic Router exists, otherwise the app ignores it completely.

```python
from fastapi import FastAPI
from backend.routers.topic_router import router as topic_router

# The main application!
app = FastAPI()

# We "Include" the router. Now the app listens for /topics requests!
app.include_router(topic_router)
```

---

## 3. Summary

When a user tries to create a Topic:
1. The **Router** (`topic_router.py`) receives the incoming internet traffic.
2. The **Schema** (`topic_schema.py`) automatically jumps in and checks if the incoming data is valid (e.g. title is not blank).
3. The Router passes the data down to the **Service** (`topic_service.py`).
4. The Service applies business rules (e.g. assigning a default difficulty of 1) and formats the data into a **Model** (`topic.py`).
5. The Service hands the model down to the **Repository** (`topic_repository.py`).
6. The Repository writes raw SQL and safely commits it to the **Database**.
7. The Database confirms it saved. The success bubbles all the way back up to the Router, which replies `200 OK` to the user's browser!
