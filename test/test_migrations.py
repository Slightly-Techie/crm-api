import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest
from sqlalchemy import text

from db.models.users import User

VERSIONS = Path(__file__).resolve().parent.parent / "Alembic" / "versions"


def load_migration(filename):
    spec = importlib.util.spec_from_file_location(filename, VERSIONS / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def run_profile_links_migration(session, monkeypatch):
    migration = load_migration("e7a1c4b9d2f0_normalise_profile_links.py")
    # Run the migration's SQL on the test database, the way Alembic would.
    monkeypatch.setattr(migration, "op", SimpleNamespace(execute=lambda sql: session.execute(text(sql))))

    def run():
        migration.upgrade()
        session.commit()
        session.expire_all()

    return run


def stored_links(session, user_id):
    user = session.get(User, user_id)
    return {
        "github_profile": user.github_profile,
        "twitter_profile": user.twitter_profile,
        "linkedin_profile": user.linkedin_profile,
        "portfolio_url": user.portfolio_url,
    }


def store_links(session, user_id, **links):
    user = session.get(User, user_id)
    for column, value in links.items():
        setattr(user, column, value)
    session.commit()


@pytest.mark.parametrize("stored, expected", [
    ("ransfordgenesis", "https://github.com/ransfordgenesis"),
    ("kobi-ampem", "https://github.com/kobi-ampem"),
    ("@kobi-ampem", "https://github.com/kobi-ampem"),
    ("  kobi-ampem\n", "https://github.com/kobi-ampem"),
    ("github.com/kobi-ampem", "https://github.com/kobi-ampem"),
    ("https://github.com/kobi-ampem", "https://github.com/kobi-ampem"),
    ("N/A", None),
    ("None", None),
    ("None yet", None),
    ("https://", None),
])
def test_github_profile_migration(session, test_user, run_profile_links_migration, stored, expected):
    store_links(session, test_user["id"], github_profile=stored)

    run_profile_links_migration()

    assert stored_links(session, test_user["id"])["github_profile"] == expected


@pytest.mark.parametrize("stored, expected", [
    ("N/A", None),
    ("None yet", None),
    ("-", None),
    ("kobi-ampem", None),
    ("https://", None),
    ("kobi.dev", "https://kobi.dev"),
    ("//kobi.dev", "https://kobi.dev"),
    ("http://kobi.dev", "http://kobi.dev"),
    ("javascript:alert(1)", None),
    ("   ", None),
])
def test_other_profile_links_migration(session, test_user, run_profile_links_migration, stored, expected):
    store_links(session, test_user["id"], portfolio_url=stored, twitter_profile=stored, linkedin_profile=stored)

    run_profile_links_migration()

    links = stored_links(session, test_user["id"])
    assert links["portfolio_url"] == expected
    assert links["twitter_profile"] == expected
    assert links["linkedin_profile"] == expected
