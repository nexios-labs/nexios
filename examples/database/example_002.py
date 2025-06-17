import datetime
from contextlib import asynccontextmanager

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from nexios import NexiosApp
from nexios.middleware.base import BaseMiddleware

# Database configuration
DATABASE_URL = "sqlite+aiosqlite:///./example_async.db"

# SQLAlchemy setup
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Declarative base class
Base = declarative_base()


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


# Database dependency
@asynccontextmanager
async def get_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Initialize app
app = NexiosApp()


# Database initialization middleware
class AsyncDatabaseMiddleware(BaseMiddleware):
    async def __call__(self, request, response, next):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return await next()


app.add_middleware(AsyncDatabaseMiddleware())


@app.post("/notes")
async def create_note(request, response):
    data = await request.json

    async with get_session() as session:
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
async def list_notes(request, response):
    show_private = request.query_params.get("show_private", "false").lower() == "true"

    async with get_session() as session:
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
async def get_note(request, response):
    note_id = request.path_params["note_id"]

    async with get_session() as session:
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
async def update_note(request, response):
    note_id = request.path_params["note_id"]
    data = await request.json

    async with get_session() as session:
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
async def delete_note(request, response):
    note_id = request.path_params["note_id"]

    async with get_session() as session:
        note = await session.get(Note, note_id)

        if not note:
            return response.json({"error": "Note not found"}, status_code=404)

        await session.delete(note)
        await session.commit()

        return response.json({"message": "Note deleted successfully", "id": note_id})
