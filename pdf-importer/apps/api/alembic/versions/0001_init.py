"""init schema

Revision ID: 0001_init
Revises:
Create Date: 2026-02-12
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "model_definitions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("json_schema", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_model_definitions_id"), "model_definitions", ["id"], unique=False)

    op.create_table(
        "import_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("model_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("ocr_text", sa.Text(), nullable=True),
        sa.Column("extracted_json", sa.Text(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["model_id"], ["model_definitions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_import_records_id"), "import_records", ["id"], unique=False)
    op.create_index(op.f("ix_import_records_model_id"), "import_records", ["model_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_import_records_model_id"), table_name="import_records")
    op.drop_index(op.f("ix_import_records_id"), table_name="import_records")
    op.drop_table("import_records")
    op.drop_index(op.f("ix_model_definitions_id"), table_name="model_definitions")
    op.drop_table("model_definitions")
