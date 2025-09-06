import datetime
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from nexios import Depends, NexiosApp
from nexios.types import Request, Response, State

# Database configuration
DATABASE_URL = "sqlite+aiosqlite:///./example_async.db"

# Declarative base class
Base = declarative_base()


# SQLAlchemy setup
class Database:
    def __init__(self, db_url: str):
        self.engine: Optional[AsyncEngine] = None
        self.async_session: Optional[async_scoped_session] = None
        self.db_url = db_url

    async def connect(self):
        if self.engine is None:
            self.engine = create_async_engine(self.db_url, echo=True)
            self.async_session = async_scoped_session(
                sessionmaker(
                    self.engine,
                    class_=AsyncSession,
                    expire_on_commit=False,
                ),
                scopefunc=lambda: None,  # This is a simple implementation
            )

            # Create tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    async def get_session(self) -> AsyncSession:
        if self.async_session is None:
            raise RuntimeError("Database is not connected")
        return self.async_session()

    async def close(self):
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.async_session = None


# Define models
class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )


# Application lifespan
@asynccontextmanager
async def lifespan(app: NexiosApp) -> AsyncGenerator[State, None]:
    # Startup: Initialize database connection
    db = Database(DATABASE_URL)
    await db.connect()

    # Make database available to routes
    state = State()
    state.db = db

    yield state  # Application runs here

    # Cleanup: Close database connection
    await db.close()


# Initialize app with lifespan
app = NexiosApp(lifespan=lifespan)


# Dependency to get database session
async def get_db_session(state: State) -> AsyncSession:
    db: Database = state.db
    return await db.get_session()


@app.post("/notes")
async def create_note(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
):
    data = await request.json()

    note = Note(
        title=data["title"],
        content=data["content"],
        is_public=data.get("is_public", False),
    )
    session.add(note)
    await session.commit()
    await session.refresh(note)

    return response.json(
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "is_public": note.is_public,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat(),
        },
        status_code=201,
    )


@app.get("/notes")
async def list_notes(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
):
    show_private = request.query_params.get("show_private", "false").lower() == "true"

    query = session.query(Note)
    if not show_private:
        query = query.filter(Note.is_public)

    notes = await query.order_by(Note.created_at.desc()).all()

    return response.json(
        [
            {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "is_public": note.is_public,
                "created_at": note.created_at.isoformat(),
                "updated_at": note.updated_at.isoformat(),
            }
            for note in notes
        ]
    )


@app.get("/notes/{note_id}")
async def get_note(
    request: Request,
    response: Response,
    note_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    note = await session.get(Note, note_id)

    if not note:
        return response.json({"error": "Note not found"}, status_code=404)

    if not note.is_public:
        return response.json({"error": "Note is private"}, status_code=403)

    return response.json(
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "is_public": note.is_public,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat(),
        }
    )


@app.put("/notes/{note_id}")
async def update_note(
    request: Request,
    response: Response,
    note_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    data = await request.json()
    note = await session.get(Note, note_id)

    if not note:
        return response.json({"error": "Note not found"}, status_code=404)

    # Update fields
    if "title" in data:
        note.title = data["title"]
    if "content" in data:
        note.content = data["content"]
    if "is_public" in data:
        note.is_public = data["is_public"]

    await session.commit()
    await session.refresh(note)

    return response.json(
        {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "is_public": note.is_public,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat(),
        }
    )


@app.delete("/notes/{note_id}")
async def delete_note(
    request: Request,
    response: Response,
    note_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    note = await session.get(Note, note_id)

    if not note:
        return response.json({"error": "Note not found"}, status_code=404)

    await session.delete(note)
    await session.commit()

    return response.json({"message": "Note deleted successfully", "id": note_id})
