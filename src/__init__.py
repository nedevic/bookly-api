import sys

sys.dont_write_bytecode = True  # this is to prevent python from generating caches

# from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.endpoints.auth.routes import auth_router
from src.endpoints.books.routes import book_router
from src.endpoints.reviews.routes import review_router
from src.endpoints.tags.routes import tag_router

# from src.db.main import init_db

# @asynccontextmanager
# async def life_span(app: FastAPI):
#     print("server is started")
#     await init_db()
#     yield
#     print("server has been stopped")


VERSION = "v1"

app = FastAPI(
    title="Bookly",
    description="A REST API for a book review web service.",
    version=VERSION,
    # lifespan=life_span,
)

app.include_router(auth_router, prefix=f"/api/{VERSION}/auth", tags=["auth"])
app.include_router(book_router, prefix=f"/api/{VERSION}/books", tags=["books"])
app.include_router(review_router, prefix=f"/api/{VERSION}/reviews", tags=["reviews"])
app.include_router(tag_router, prefix=f"/api/{VERSION}/tags", tags=["tags"])
