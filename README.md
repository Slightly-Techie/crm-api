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
- [TODO](#todo)
- [About](#about)
- [Getting Started](#getting_started)
- [Running the tests](#tests)
- [Project Structure](#structure)
- [Contributing](#contributing)
- [Usage](#usage)
- [Built Using](#built_using)
- [Team](#team)

## Todo <a name = "todo"></a>
See [TODO](./docs/TODO.md)

## About <a name = "about"></a>
This project is a CRM API for Slightly Techie. It is built using [these](#built_using) technologies.

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
POSTGRES_USER= #e.g postgres
POSTGRES_PASSWORD= #e.g password123
POSTGRES_SERVER= #e.g localhost
POSTGRES_PORT= #e.g 5432
POSTGRES_DB= #e.g st_crm_db
SECRET= #notasecretkey
BASE_URL= #http://127.0.0.1:8080/
EMAIL_SENDER=someawesomeemail@gmail.com
EMAIL_PASSWORD=xxxxxxxxxxx
EMAIL_SERVER=smtp.gmail.com
EMAIL_PORT=587
AWS_ACCESS_KEY=xxxxxxxxxxxxx
AWS_SECRET_KEY=xxxxxxxxxxx
AWS_BUCKET_NAME=stncrmutilities
AWS_REGION=eu-west-1
URL_PATH=/users/reset-password/new-password
```

#### Step 6: Create a `test.env` file in the root directory and add the following environment variables

```bash
POSTGRES_USER= #e.g postgres
POSTGRES_PASSWORD= #e.g password123
POSTGRES_SERVER= #e.g localhost
POSTGRES_PORT= #e.g 5432
POSTGRES_DB= #e.g st_crm_db
```

#### Step 7: Start the uvicorn server

```bash
uvicorn app:app --reload
```

### Step 8: Interact with the Database
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
├───docs
│       TODO.md
│
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
- [Postgres](https://www.postgresql.org/) - Database
- [Fly.io](https://fly.io/) - Cloud Hosting
- [Poetry](https://python-poetry.org/) - Python Package Manager
- [Docker](https://www.docker.com/) - Containerization
- [SqlAlchemy](https://www.sqlalchemy.org/) - ORM
- [Alembic](https://alembic.sqlalchemy.org/en/latest/) - Database Migration
- [Pytest](https://docs.pytest.org/en/6.2.x/) - Testing Framework

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