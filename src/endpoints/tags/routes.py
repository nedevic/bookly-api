from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.endpoints.auth.dependencies import AccessTokenBearer, RoleChecker
from src.endpoints.auth.utils import UserRoles
from src.endpoints.books.dependencies import owns_book_or_admin
from src.endpoints.tags.service import TagException, TagNotFoundException, TagService
from src.schemas.books_schemas import Book
from src.schemas.tags_schemas import Tag, TagAdd, TagCreate, TagUpdate

tag_router = APIRouter()
tag_service = TagService()
access_token_bearer = AccessTokenBearer()
admin_role_checker = RoleChecker(allowed_roles=[UserRoles.ADMIN.value])


@tag_router.get("/", response_model=List[Tag])
async def get_all_tags(
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
):
    return await tag_service.get_all_tags(session)


@tag_router.post(
    "/book/{book_uid}",
    status_code=status.HTTP_201_CREATED,
    response_model=Book,
)
async def add_tags_for_book(
    book_id: str,
    tag_data: TagAdd,
    session: AsyncSession = Depends(get_session),
    _=Depends(owns_book_or_admin),
):
    try:
        return await tag_service.add_tags_for_book(
            book_uid=book_id,
            review_data=tag_data,
            session=session,
        )
    except TagException as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        )


@tag_router.post("/", status_code=status.HTTP_201_CREATED, response_model=Tag)
async def create_tag(
    tag_data: TagCreate,
    session: AsyncSession = Depends(get_session),
    token_details=Depends(access_token_bearer),
) -> dict:
    return await tag_service.create_tag(tag_data, session)


@tag_router.patch("/{tag_id}", response_model=Tag)
async def update_tag(
    tag_id: str,
    tag_update_data: TagUpdate,
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_role_checker),
) -> dict:
    try:
        return await tag_service.update_tag(tag_id, tag_update_data, session)
    except TagNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@tag_router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: str,
    session: AsyncSession = Depends(get_session),
    _=Depends(admin_role_checker),
):
    try:
        await tag_service.delete_tag(tag_id, session)
    except TagNotFoundException as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
