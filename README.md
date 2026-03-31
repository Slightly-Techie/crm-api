<h3 align="center">CRM API</h3>

<div align="center">

  ![Status](https://img.shields.io/badge/status-active-success.svg)
  ![GitHub issues](https://img.shields.io/github/issues/Slightly-Techie/crm-api?color=yellow)
  ![GitHub pull requests](https://img.shields.io/github/issues-pr/Slightly-Techie/crm-api?color=success)
  [![License](https://img.shields.io/badge/license-Proprietary-blue.svg)](/LICENSE)


</div>

---

<p align="center"> Backend API for Slightly Techie CRM
    <br> 
</p>

## 📝 Table of Contents
- [About](#about)
- [Getting Started](#getting_started)
- [Running the tests](#tests)
- [Project Structure](#structure)
- [Contributing](#contributing)
- [Usage](#usage)
- [Built Using](#built_using)
- [Team](#team)


## About <a name = "about"></a>
The Slightly Techie CRM API is a comprehensive backend service for managing customer relationships, user profiles, projects, skills, announcements, and more. It provides RESTful endpoints for all CRM operations. and includes features like:

Built with FastAPI for high performance and automatic API documentation.

### Automatic Initialization on Startup

When the application starts, it automatically initializes essential seed data:

**Roles**
- Admin
- User  
- Guest

**Stacks (Technical Specializations)**
- Backend
- Frontend
- Fullstack
- Mobile
- UI/UX
- DevOps
- Data Science

**Signup Endpoint**
- Created automatically for user registration tracking

This ensures the application is ready to use without manual database setup for these core entities.

## 🏁 Getting Started <a name = "getting_started"></a>
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites
- Poetry: Dependency manager for Python.
- Postgres: A relational database.
- Python 3.10^: The Python programming language.
- AutoPEP8: An auto-formatter for Python code.


### Setting up a development environment
#### Step 1: Clone the repository

```bash
https://github.com/Slightly-Techie/crm-api.git
```

or with GithubCLI
  
```bash
gh repo clone Slightly-Techie/crm-api
```

#### step 2: Install poetry if you don't have it already

```bash
# Linux, macOS, Windows (WSL)
curl -sSL https://install.python-poetry.org | python3 -
```

```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

> _Note: If you have installed Python through the Microsoft Store, replace py with python in the command above._

> _Reference: [Poetry Installation](https://python-poetry.org/docs/#installation)_

#### step 3: Create a virtual environment

```bash
virtualenv crmenv
```
OR by using the virtualenvwrapper
```bash
  mkvirtualenv crmenv
```
Activate the virtual environment with 
```bash
  source crmenv/bin/activate
```

#### Step 4: Install dependencies

```
pip install -r requirements.txt
```

> Note to add a package to the project, run

```bash
pip install <package-name>
```

#### Step 5: Create a `.env` file in the project's root directory and add the following environment variables, replacing the placeholders with your specific values:

```bash
# Database Configuration
POSTGRES_USER=postgres              # e.g., postgres
POSTGRES_PASSWORD=password123       # e.g., your_secure_password
POSTGRES_SERVER=localhost           # e.g., localhost or your_db_host
POSTGRES_PORT=5432                 # Default PostgreSQL port
POSTGRES_DB=st_crm_db              # e.g., st_crm_db
POSTGRES_DB_TEST=st_crm_db_test    # Test database

# Security & Authentication
SECRET=your_secret_key_here         # JWT secret key (use a strong value)
REFRESH_SECRET=your_refresh_key     # JWT refresh secret key (use a strong value)

# Server Configuration
BASE_URL=http://localhost:3000      # Frontend URL for CORS and links
URL_PATH=/users/reset-password/new-password

# Email Configuration (Gmail SMTP)
EMAIL_SENDER=someawesomeemail@gmail.com
EMAIL_PASSWORD=your_app_password    # Use Gmail app-specific password
EMAIL_SERVER=smtp.gmail.com
EMAIL_PORT=587

# Cloudinary Configuration (Media Storage)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

#### Step 6: Create a `test.env` file in the root directory and add the following environment variables

```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=st_crm_db_test

# Optional: Add these if running tests that involve media uploads
SECRET=test_secret_key
REFRESH_SECRET=test_refresh_secret
CLOUDINARY_CLOUD_NAME=your_test_cloud_name
CLOUDINARY_API_KEY=your_test_api_key
CLOUDINARY_API_SECRET=your_test_api_secret
```

#### Step 7: Start the uvicorn server

```bash
uvicorn app:app --reload
```

> **⚠️ Important - First Time Setup**: 
> On the **first startup**, the application automatically initializes seed data:
> - **Roles**: Admin, User, Guest
> - **Stacks**: Backend, Frontend, Fullstack, Mobile, UI/UX, DevOps, Data Science
> - **Signup Endpoint**: Required for user registration
>
> This is handled by the `startup_event()` in `app.py` which is enabled via:
> ```python
> app.add_event_handler("startup", startup_event)
> ```
> 
> If this event handler is commented out and you need to re-initialize the database, you can:
> - Uncomment `app.add_event_handler("startup", startup_event)` in `app.py`, OR
> - Run manually in Python:
>   ```python
>   from db.database import create_roles, create_stacks
>   create_roles()
>   create_stacks()
>   ```

### Step 8: (Optional) Populate Test Data and Update Users

To create 20 dummy users for testing:

```bash
python create_dummy_users.py
```

This creates test users with credentials:
- Email: `user1@slightlytechie.com` → `user20@slightlytechie.com`
- Password: `TestPassword123!` (for all)
- Users are distributed across different stacks

**Additional user management scripts** (if needed):

```bash
# Update all users' status from TO_CONTACT to ACCEPTED
python update_users_status.py

# Update all users' role_id to 2 (User role)
python update_users_role.py
```

### Step 9: Interact with the Database
To interact with the database, you can use tools like psql, pgAdmin or any database client that supports PostgreSQL. Here are some basic commands:

- Connect to the database:

```bash
psql -U postgres -d st_crm_db
```

- List all tables:

```bash
\d
```

- Execute SQL queries:

```bash
SELECT * FROM table_name;
```


## 🔧 Running the tests <a name = "tests"></a>
To ensure the code is functioning correctly, you can run tests by executing the following command:

```bash
pytest
```

> Make sure your `test.env` file is correctly configured with test-specific environment variables.

## Running the project in Docker-Compose
* Clone the project and from the main, create your feature branch if you are about to make changes. Else stay on the main branch
* From the `.env.sample` create a `.env` file with the correct credentials
* Ensure you have docker and docker compose installed on your local system
* To build the docker image use
```bash
  docker-compose -f docker-compose.dev.yml build
```
* To start the services
```bash
  doker-compose -f docker-compose.dev.yml up
```
* A combination of build and start command is 
```bash
  docker-compose -f docker-compose.dev.yml up --build
```
* To run tests 
```bash
  docker-compose -f docker-compose.dev.yml run --rm app sh -c "python -m pytest test"
```
## ⚙️ Project Structure <a name = "structure"></a>
```s
│   app.py
│   Dockerfile
│   fly.toml
│   poetry.lock
│   pyproject.toml
│   README.md
│   test_app.py
│   __init__.py
│
├───.github
│   └───workflows
│           build.yml
│           fly.yml
│
├───Alembic
│   │   env.py
│   │   README
│   │   script.py.mako
│
├───api
│   │   __init__.py
│   │
│   ├───api_models
│   │   │   announcements.py
│   │   │   skills.py
│   │   │   stacks.py
│   │   │   tags.py
│   │   │   user.py
│   │
│   ├───routes
│   │   │   announcements.py
│   │   │   auth.py
│   │   │   feeds.py
│   │   │   profile_page.py
│   │   │   skills.py
│   │   │   stacks.py
│   │   │   tags.py
│   │   │   techieotm.py
│   │   │   __init__.py
│
├───core
│   │   config.py
│   │   exceptions.py
│
├───db
│   │   database.py
│   │   __init__.py
│   ├───models
│   │    users.py
│   └───repository
│        users.py
├───test
│   │   conftest.py
│   │   test_announcements.py
│   │   test_auth.py
│   │   test_feeds.py
│   │   test_profile_page.py
│   │   test_skills.py
│   │   test_stacks.py
│   │   test_tags.py
│   │   test_techieotm.py
│   │   test_users.py
│   │   utils_test.py
│   │   __init__.py
│
└───utils
    │   oauth2.py
    │   permissions.py
    │   utils.py
    │   __init__.py


```

## ✏️ Contributing <a name = "contributing"></a>
We welcome contributions from the community. To contribute to the CRM API project, follow these guidelines:

### Coding Standards
- Follow the PEP 8 coding style for Python.
- Ensure your code is well-documented with clear comments and docstrings.
- Use meaningful variable and function names.

### Branch Naming Conventions
**Create a new branch for your feature or bug fix using the format below.**
```bash
git checkout -b <initials/issue_no/feature> eg. # RG/121/Fixed-login-page
```

### Pull Requests
- Commit your changes to your branch with a clear and descriptive commit message:
```bash
git add .
git commit -m "Made this in this file"
```
- Push your branch to the repository on GitHub:
```bash
git push -u origin <name-of-branch>
```
- Open a pull request in the original repository, providing a detailed description of your changes and any relevant information.

> please try building the project on your local machine to confirm everything works before pushing...Thanks

## 🎈 Usage <a name="usage"></a>
visit the API Documentation at [https://crm-api.fly.dev/docs](https://crm-api.fly.dev/docs)


## ⛏️ Built Using <a name = "built_using"></a>
- [FastAPI](https://fastapi.tiangolo.com/) - Python Framework
- [PostgreSQL](https://www.postgresql.org/) - Relational Database
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM (Object-Relational Mapping)
- [Alembic](https://alembic.sqlalchemy.org/en/latest/) - Database Migration Tool
- [Cloudinary](https://cloudinary.com/) - Media Storage & CDN
- [Pytest](https://docs.pytest.org/en/6.2.x/) - Testing Framework
- [Poetry](https://python-poetry.org/) - Python Dependency Manager
- [Docker](https://www.docker.com/) - Containerization
- [Fly.io](https://fly.io/) - Cloud Hosting Platform

## ✍️ Team <a name = "team"></a>
- [@RansfordGenesis](https://github.com/RansfordGenesis)
- [@KwesiDadson](https://github.com/blitzblade)
- [@EmmanuelTiboah](https://github.com/eeTiboah)
- [@EssilfieQuansah](https://github.com/benessilfie)
- [@RachealKuranchie](https://github.com/Racheal777)
- [@JerryAgbesi](https://github.com/JerryAgbesi)
- [@Kryzbone](https://github.com/kryzbone)
- [@GreatnessMensah](https://github.com/greatnessmensah)
- [@CozyBrian](https://github.com/CozyBrian)
- [@Tonny-Bright](https://github.com/TMCreme)