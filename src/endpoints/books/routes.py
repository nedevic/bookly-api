from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.endpoints.auth.dependencies import AccessTokenBearer
from src.endpoints.books.dependencies import owns_book_or_admin
from src.endpoints.books.service import BookNotFoundException, BookService
from src.schemas.book_relations_schemas import BookRelations
from src.schemas.books_schemas import Book, BookCreate, BookUpdate

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()


@book_router.get("/", response_model=List[Book])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
):
    return await book_service.get_all_books(session)


@book_router.get("/user/{user_uid}", response_model=List[Book])
async def get_user_books(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
):
    return await book_service.get_user_books(user_uid, session)


@book_router.get("/{book_id}", response_model=BookRelations)
async def get_book(
    book_id: str,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
) -> dict:
    try:
        return await book_service.get_book(book_id, session)
    except BookNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found!"
        )


@book_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Book)
async def create_book(
    book_data: BookCreate,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
) -> dict:
    user_id = token_details["user"]["user_uid"]
    return await book_service.create_book(book_data, user_id, session)


@book_router.patch("/{book_id}", response_model=Book)
async def update_book(
    book_id: str,
    book_update_data: BookUpdate,
    session: AsyncSession = Depends(get_session),
    _=Depends(owns_book_or_admin),
) -> dict:
    try:
        return await book_service.update_book(book_id, book_update_data, session)
    except BookNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found!"
        )


@book_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: str,
    session: AsyncSession = Depends(get_session),
    _=Depends(owns_book_or_admin),
):
    try:
        await book_service.delete_book(book_id, session)
    except BookNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found!"
        )
