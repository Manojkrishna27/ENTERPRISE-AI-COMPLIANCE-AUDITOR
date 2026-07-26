"""Initial Schema Revision

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-07-26 12:00:00.000000

"""

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Schema creation handled by SQLAlchemy Base.metadata.create_all for local,
    # and explicit Alembic migration steps for production.
    pass


def downgrade():
    pass
