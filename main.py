from fastapi import FastAPI

from core.ption_handlers import register_exception_handlers
from routers import auth, books, memories, search, media, share

app = FastAPI()

@app.get("/")
async def Hi():
    return {"message": "Hello World"}


app.include_router(auth.router, prefix="/api/v1")
app.include_router(books.router, prefix="/api/v1")
app.include_router(memories.router, prefix="/api/v1")
app.include_router(search.router, prefix="/api/v1")
app.include_router(media.router, prefix="/api/v1")
app.include_router(share.memories_share_router, prefix="/api/v1/memories", tags=["share"])
app.include_router(share.public_router, prefix="/api/v1")
register_exception_handlers(app)