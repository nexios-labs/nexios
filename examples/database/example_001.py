import sqlite3
from contextlib import contextmanager

from nexios import NexiosApp
from nexios.middleware.base import BaseMiddleware

app = NexiosApp()

# Database setup
DB_PATH = "example.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        )


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(self, request, response, next):
        # Initialize database if needed
        init_db()
        return await next()


# Add database middleware
app.add_middleware(DatabaseMiddleware())


@app.get("/todos")
async def list_todos(request, response):
    with get_db() as db:
        todos = db.execute("SELECT * FROM todos ORDER BY created_at DESC").fetchall()
        return response.json(
            [
                {
                    "id": todo["id"],
                    "title": todo["title"],
                    "completed": bool(todo["completed"]),
                    "created_at": todo["created_at"],
                }
                for todo in todos
            ]
        )


@app.post("/todos")
async def create_todo(request, response):
    data = await request.json
    title = data.get("title")

    if not title:
        return response.json({"error": "Title is required"}, status_code=400)

    with get_db() as db:
        cursor = db.execute("INSERT INTO todos (title) VALUES (?)", (title,))
        db.commit()

        # Get the created todo
        todo = db.execute(
            "SELECT * FROM todos WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()

        return response.json(
            {
                "id": todo["id"],
                "title": todo["title"],
                "completed": bool(todo["completed"]),
                "created_at": todo["created_at"],
            },
            status_code=201,
        )


@app.put("/todos/{todo_id}")
async def update_todo(request, response):
    todo_id = request.path_params["todo_id"]
    data = await request.json

    with get_db() as db:
        # Check if todo exists
        todo = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()

        if not todo:
            return response.json({"error": "Todo not found"}, status_code=404)

        # Update fields
        updates = []
        values = []
        if "title" in data:
            updates.append("title = ?")
            values.append(data["title"])
        if "completed" in data:
            updates.append("completed = ?")
            values.append(1 if data["completed"] else 0)

        if updates:
            values.append(todo_id)
            db.execute(f"UPDATE todos SET {', '.join(updates)} WHERE id = ?", values)
            db.commit()

        # Get updated todo
        todo = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()

        return response.json(
            {
                "id": todo["id"],
                "title": todo["title"],
                "completed": bool(todo["completed"]),
                "created_at": todo["created_at"],
            }
        )


@app.delete("/todos/{todo_id}")
async def delete_todo(request, response):
    todo_id = request.path_params["todo_id"]

    with get_db() as db:
        # Check if todo exists
        todo = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()

        if not todo:
            return response.json({"error": "Todo not found"}, status_code=404)

        # Delete todo
        db.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        db.commit()

        return response.json({"message": "Todo deleted successfully", "id": todo_id})
