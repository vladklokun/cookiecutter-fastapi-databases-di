import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as sa_psql


_metadata = sa.MetaData()


healthchecks = sa.Table(
    "healthchecks",
    _metadata,
    sa.Column(
        "id",
        sa_psql.UUID(),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    ),
    sa.Column("status", sa.Text(), nullable=False, comment="Status of the healthcheck"),
    comment="A table for health checks.",
)
