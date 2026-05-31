"""empty message

Revision ID: 2f28bcb629b0
Revises:
Create Date: 2026-05-28 22:57:14.970276

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "2f28bcb629b0"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
