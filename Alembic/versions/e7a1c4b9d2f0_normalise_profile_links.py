"""Normalise stored profile links

Revision ID: e7a1c4b9d2f0
Revises: d4e5f6a7b8c9
Create Date: 2026-11-04 10:00:00.000000

Profile links saved without a scheme ("github.com/kobi") were rendered as
relative links (app.slightlytechie.com/github.com/kobi). New values are now
normalised by the API; this fixes the values already stored, using the same
rules as utils.utils.normalize_profile_url:

- empty or blank: NULL
- starts with "//": "https:" is added
- has a scheme other than http or https ("javascript:", "mailto:"): NULL
- no scheme: "https://" is added

The SQL is written out here on purpose, so the migration keeps working even
if the Python helper changes later.
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'e7a1c4b9d2f0'
down_revision = 'd4e5f6a7b8c9'
branch_labels = None
depends_on = None

PROFILE_LINK_COLUMNS = ("github_profile", "twitter_profile", "linkedin_profile", "portfolio_url")

# A scheme followed by ":" and not a digit (a digit means a port, as in "github.com:443").
HAS_SCHEME = r"'^[a-zA-Z][a-zA-Z0-9+.-]*:[^0-9]'"
HAS_HTTP_SCHEME = r"'^https?://'"


def upgrade() -> None:
    for column in PROFILE_LINK_COLUMNS:
        # Trim spaces, tabs and newlines; blank becomes NULL.
        op.execute(f"UPDATE users SET {column} = NULLIF(btrim({column}, E' \\t\\r\\n'), '')")
        # Protocol-relative links: "//example.com" -> "https://example.com".
        op.execute(f"UPDATE users SET {column} = 'https:' || {column} WHERE {column} LIKE '//%'")
        # Unsafe schemes are removed.
        op.execute(
            f"UPDATE users SET {column} = NULL "
            f"WHERE {column} ~ {HAS_SCHEME} AND {column} !~* {HAS_HTTP_SCHEME}"
        )
        # No scheme at all: add https://.
        op.execute(
            f"UPDATE users SET {column} = 'https://' || {column} "
            f"WHERE {column} IS NOT NULL AND {column} !~ {HAS_SCHEME}"
        )


def downgrade() -> None:
    # Data-only fix: the original values are not kept, so there is nothing to undo.
    pass
