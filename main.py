from fastapi import FastAPI

from core.ption_handlers import register_exception_handlers
from routers import auth, books, memories

app = FastAPI()

@app.get("/")
async def Hi():
    return {"message": "Hello World"}


app.include_router(auth.router, prefix="/api/v1")
app.include_router(books.router, prefix="/api/v1")
app.include_router(memories.router, prefix="/api/v1")
register_exception_handlers(app)