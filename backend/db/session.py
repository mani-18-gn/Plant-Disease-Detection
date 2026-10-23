import datetime
import uuid
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB, UUID
from typing import Generator
from backend.config import settings

# SQLite compatibility shims for PostgreSQL-specific types
@compiles(JSONB, "sqlite")
def _compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

@compiles(UUID, "sqlite")
def _compile_uuid_sqlite(type_, compiler, **kw):
    return "TEXT"

is_sqlite = settings.DATABASE_URL.startswith("sqlite")

if is_sqlite:
    engine_kwargs: dict[str, object] = {"connect_args": {"check_same_thread": False}}
    if ":memory:" in settings.DATABASE_URL:
        engine_kwargs["poolclass"] = StaticPool

    engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

    @event.listens_for(engine, "connect")
    def _sqlite_connect(dbapi_connection, connection_record):
        # Register PostgreSQL helper functions in SQLite
        dbapi_connection.create_function(
            "now", 0, lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
        dbapi_connection.create_function("gen_random_uuid", 0, lambda: str(uuid.uuid4()))
        from pathlib import Path
        db_dir = Path(__file__).resolve().parent.parent / "data" / "sqlite"
        db_dir.mkdir(parents=True, exist_ok=True)
        cursor = dbapi_connection.cursor()
        for schema in ["core", "agronomy", "env", "market", "logs"]:
            schema_file = (db_dir / f"{schema}.sqlite3").as_posix()
            cursor.execute(f"ATTACH DATABASE '{schema_file}' AS {schema}")
        cursor.close()

    # Pre-create all schema tables for SQLite
    from backend.db.base import Base
    import backend.db.models  # noqa
    Base.metadata.create_all(bind=engine)
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@event.listens_for(SessionLocal, "before_flush")
def _auto_populate_uuid(session, flush_context, instances):
    for obj in session.new:
        if hasattr(obj, "id") and getattr(obj, "id", None) is None:
            obj.id = str(uuid.uuid4())
        if hasattr(obj, "planting_date") and isinstance(getattr(obj, "planting_date", None), str):
            try:
                obj.planting_date = datetime.date.fromisoformat(obj.planting_date)
            except Exception:
                pass


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for yielding DB sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

