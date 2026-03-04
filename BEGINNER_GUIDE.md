# A Beginner's Guide to Our Backend

Welcome! Since you're new to backend development and FastAPI, this guide is written just for you. We'll break down how your project is organized in simple terms, so you can easily understand what each part does.

---

## 1. The Big Picture: What is a Backend?

Imagine a restaurant:
* Validating your order, cooking the food, and managing the kitchen is the **Backend**. 
* The **Frontend** (your React/Next.js app or mobile app) is the waiter who takes your order and brings you the food.
* The **Database** is the pantry where all ingredients (data) are stored.
* **FastAPI** is the framework we use to build this kitchen. It's fast, modern, and uses Python!

---

## 2. Breaking Down the Folders

Here's how our "kitchen" is organized so things don't get messy:

### `core/` - The Foundation
Think of this as the building's infrastructure (electricity, plumbing, locks on the doors).
* `config.py`: Reads your `.env` file to know secret passwords and settings.
* `database.py`: Connects your app to the PostgreSQL database so you can save and read data.
* `firebase.py`: The security guard. It checks if users who are trying to log in are actually who they say they are.
* `dependencies.py`: Handy tools that any part of your app can ask for (like "give me the database" or "tell me which user made this request").

### `main.py` - The Restaurant Manager
This is the main entry point to your application. It brings everything together.
* It starts the FastAPI "kitchen".
* It sets up the security guard (Firebase) when the restaurant opens.
* It registers all the Waiters (Routers) so that when an order (request) comes in, the manager knows exactly who to give it to.
* It has a simple "Health Check" endpoint (like asking the manager "Are you open?") to make sure everything is running smoothly.

### `routers/` - The Waiters (Endpoints)
These files act as the URLs your frontend will call.
* If the frontend wants to get a user's profile, it calls the waiter at `/profile`. The `profile.py` router takes the request and passes it to the right place.

### `models/` - The Database Layout
This tells the database what your tables look like.
* `user.py` might say: "A User has an ID, a name, and an email."
* This uses *SQLAlchemy*, which translates Python code into SQL (database language) automatically!

### `schemas/` - The Bouncers (Pydantic)
Before data enters or leaves your app, it must be checked.
* **Pydantic** is a library that checks if the data is correct. 
* If someone tries to create an account with an age of `"banana"`, the schema will block it and say "Age must be a number!"

### `services/` - The Chefs (Business Logic)
This is where the actual work happens. The router takes an order and hands it to a service.
* If a router gets a request to "Create a new quiz session", it tells `session_service.py` to do the heavy lifting: checking the database, doing math, and talking to AI agents.

### `agents/` - The AI Specialists
Since your app is AI-powered, these are specialized workers powered by LangGraph and Gemini.
* E.g., `quiz_agent.py` knows exactly how to read a student's history and generate the perfect quiz questions for them.

### `tests/` - The Health Inspectors
Before we open the restaurant to the public, we need to make sure everything works automatically.
* A file like `test_health.py` acts like a fake customer. It automatically makes an order to the "Health Check" endpoint and double-checks that the response comes back as expected!

### `requirements.txt` & `.env` - The Instruction Manuals
* **`requirements.txt`**: A grocery list of exactly which third-party tools (and their exact versions) we need to build the app (like FastAPI, SQLAlchemy, Google Gemini tools).
* **`.env.example` & `.env`**: A list of secret passwords and keys needed to make the app work. `example` is public, while `.env` stays locked down on your machine!

---

## 3. How to Connect This Project to Your GitHub

GitHub is like a save-game system for your code. It keeps track of every change you make and lets you back it up online.

Here is the step-by-step guide to putting this project on GitHub:

### Step 1: Create a Repository on GitHub
1. Go to [GitHub.com](https://github.com) and log in.
2. Click the **"+"** icon in the top right and select **"New repository"**.
3. Name it something like `my-ai-project-backend` (or whatever you like).
4. Leave it as **Public** or **Private** (Private is safer for now).
5. **DO NOT** check any boxes like "Add a README" or "Add .gitignore". We'll do that ourselves.
6. Click **"Create repository"**.

### Step 2: Push Your Code from Your Computer
Open your terminal (Command Prompt or VS Code terminal), make sure you are inside your `THE MAIN PROJECT` folder, and run these commands one by one:

1. **Initialize Git** (Tells your folder to start tracking changes):
   ```bash
   git init
   ```

2. **Add all your files to the staging area** (Getting them ready to save):
   ```bash
   git add .
   ```

3. **Commit the changes** (Actually saving them with a message):
   ```bash
   git commit -m "First commit: Set up backend folder structure and core modules"
   ```

4. **Connect your local code to the GitHub link you just created**:
   *(Copy this exact command from the GitHub page you just created. It looks like this:)*
   ```bash
   git remote add origin https://github.com/your-username/your-repo-name.git
   ```

5. **Upload (Push) the code to GitHub**:
   ```bash
   git branch -M main
   git push -u origin main
   ```

**Important Note before you do this:** Make sure you create a `.gitignore` file so you don't accidentally push your secret passwords (like `.env`) to the internet! We can create that next if you want.
