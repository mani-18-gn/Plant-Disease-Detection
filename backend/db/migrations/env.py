"""
Alembic env.py for ArecaAgent.

Key behaviours:
- Reads DATABASE_URL from backend/config.py (pydantic-settings -> backend/.env).
  Never hardcoded here.
- Sets include_schemas=True so Alembic tracks cross-schema tables.
- Sets version_table_schema so Alembic's own version table lives in a
  dedicated 'migrations' search-path slot rather than polluting 'public'.
- Imports all SQLAlchemy models before autogenerate so metadata is populated.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, text
from alembic import context

# ── 1. Pull DATABASE_URL from pydantic-settings (reads backend/.env) ─────────
from backend.config import settings  # noqa: E402

# ── 2. Import ALL models so their metadata is registered with Base ────────────
import backend.db.models  # noqa: F401  (side-effect: populates Base.metadata)
from backend.db.base import Base  # noqa: E402

# ── 3. Standard Alembic config wiring ────────────────────────────────────────
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Inject the real URL — overrides the blank sqlalchemy.url in alembic.ini
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata


# ── 4. Migration runners ──────────────────────────────────────────────────────

def run_migrations_offline() -> None:
    """Offline mode: emit SQL to stdout without a live DB connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        version_table="alembic_version",
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Online mode: connect to the live Neon database and run migrations."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.begin() as connection:
        # Ensure the 5 schemas exist before Alembic tries to introspect them.
        # This is idempotent — safe to run on every migration run.
        for schema in ("core", "agronomy", "env", "market", "logs"):
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        connection.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            version_table="alembic_version",
            version_table_schema="public",
            compare_type=True,
            compare_server_default=True,
        )
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
