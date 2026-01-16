"""Initial schema - Create all tables

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-01-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create PropertyType enum
    property_type_enum = postgresql.ENUM(
        "Detached", "Semi-Detached", "Terraced", "Flat",
        name="propertytype",
        create_type=True
    )
    property_type_enum.create(op.get_bind(), checkfirst=True)

    # Create TransactionCategory enum
    transaction_category_enum = postgresql.ENUM(
        "Standard", "Additional",
        name="transactioncategory",
        create_type=True
    )
    transaction_category_enum.create(op.get_bind(), checkfirst=True)

    # Create OpportunityPriority enum
    opportunity_priority_enum = postgresql.ENUM(
        "High", "Medium", "Low",
        name="opportunitypriority",
        create_type=True
    )
    opportunity_priority_enum.create(op.get_bind(), checkfirst=True)

    # Create active_listings table first (referenced by properties)
    op.create_table(
        "active_listings",
        sa.Column("listing_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("external_url", sa.String(500), nullable=False, unique=True),
        sa.Column("asking_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("listing_date", sa.Date(), nullable=False),
        sa.Column("agent_name", sa.String(200), nullable=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("raw_data", postgresql.JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    # Create properties table
    op.create_table(
        "properties",
        sa.Column("uprn", sa.String(12), primary_key=True),
        sa.Column("address_bs7666", postgresql.JSONB, nullable=False),
        sa.Column("floor_area_sqft", sa.Float(), nullable=True),
        sa.Column("property_type", property_type_enum, nullable=False),
        sa.Column("epc_rating", sa.String(1), nullable=True),
        sa.Column("current_listing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("active_listings.listing_id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_properties_uprn", "properties", ["uprn"])

    # Create historical_transactions table
    op.create_table(
        "historical_transactions",
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("uprn", sa.String(12), sa.ForeignKey("properties.uprn"), nullable=False),
        sa.Column("price_paid", sa.Numeric(12, 2), nullable=False),
        sa.Column("date_of_transfer", sa.Date(), nullable=False),
        sa.Column("transaction_category", transaction_category_enum, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_historical_transactions_uprn", "historical_transactions", ["uprn"])
    op.create_index("ix_historical_transactions_date_of_transfer", "historical_transactions", ["date_of_transfer"])

    # Create valuation_metrics table
    op.create_table(
        "valuation_metrics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("uprn", sa.String(12), sa.ForeignKey("properties.uprn"), unique=True, nullable=False),
        sa.Column("current_ppsf", sa.Float(), nullable=False),
        sa.Column("market_ppsf_12m", sa.Float(), nullable=True),
        sa.Column("undervalued_index", sa.Float(), nullable=True),
        sa.Column("projected_yield", sa.Float(), nullable=True),
        sa.Column("comparable_count", sa.Integer(), nullable=False, default=0),
        sa.Column("priority", opportunity_priority_enum, nullable=True),
        sa.Column("calculated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_valuation_metrics_uprn", "valuation_metrics", ["uprn"])


def downgrade() -> None:
    op.drop_table("valuation_metrics")
    op.drop_table("historical_transactions")
    op.drop_table("properties")
    op.drop_table("active_listings")

    # Drop enums
    op.execute("DROP TYPE IF EXISTS opportunitypriority")
    op.execute("DROP TYPE IF EXISTS transactioncategory")
    op.execute("DROP TYPE IF EXISTS propertytype")
