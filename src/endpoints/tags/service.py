from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.models import Tag
from src.endpoints.books.service import BookException, BookService
from src.schemas.tags_schemas import TagAdd, TagCreate, TagUpdate

book_service = BookService()


class TagException(Exception):
    """Base class for TagService exceptions"""

    def __init__(self, message: str):
        super().__init__(message)


class TagNotFoundException(TagException):
    def __init__(self, message: str = "Tag was not found."):
        super().__init__(message)


class TagAlreadyExistsException(TagException):
    def __init__(self, message: str = "A tag with this name already exists."):
        super().__init__(message)


class TagService:
    async def get_all_tags(self, session: AsyncSession):
        statement = select(Tag).order_by(desc(Tag.created_at))
        result = await session.exec(statement)
        tags = result.all()
        return tags

    async def get_tag(self, tag_uid: str, session: AsyncSession):
        """
        Gets a tag by tag_uid. Raises TagNotFoundException if no tag is found.
        """
        statement = select(Tag).where(Tag.uid == tag_uid)
        result = await session.exec(statement)
        tag = result.first()
        if tag:
            return tag
        raise TagNotFoundException(f"Tag with id {tag_uid} was not found.")

    async def add_tags_for_book(
        self,
        book_uid: str,
        tag_data: TagAdd,
        session: AsyncSession,
    ):
        """
        Adds tags for a book. Raises TagException if not successful.
        """
        try:
            book = await book_service.get_book(book_uid, session)
            book_tag_names = [t.name for t in book.tags]
        except BookException as exc:
            raise TagException(str(exc))

        tags_to_add = []

        for tag in tag_data.tags:
            if tag.name in book_tag_names:
                continue

            result = await session.exec(select(Tag).where(Tag.name == tag.name))

            tag_to_add = result.one_or_none()
            if not tag_to_add:
                tag_to_add = Tag(name=tag.name)
                # session.add(tag)

            tags_to_add.append(tag_to_add)

        book.tags = tags_to_add

        session.add(book)
        await session.commit()
        # await session.refresh(book)
        return book

    async def create_tag(self, tag_data: TagCreate, session: AsyncSession):
        """
        Creates a tag. Raises TagAlreadyExistsException if the tag exists.
        """
        result = await session.exec(select(Tag).where(Tag.name == tag_data.name))

        tag = result.one_or_none()
        if tag:
            raise TagAlreadyExistsException()

        new_tag = Tag(name=tag_data.name)

        session.add(new_tag)
        await session.commit()
        return new_tag

    async def update_tag(
        self, tag_uid: str, update_data: TagUpdate, session: AsyncSession
    ):
        """
        Finds a tag by tag_uid and updates it.
        Raises TagNotFoundException if no tag is found.
        """
        tag_to_update = await self.get_tag(tag_uid, session)

        update_data_dict = update_data.model_dump()
        for k, v in update_data_dict.items():
            setattr(tag_to_update, k, v)

        await session.commit()
        return tag_to_update

    async def delete_tag(self, tag_uid: str, session: AsyncSession):
        """
        Finds a tag by tag_uid and deletes it.
        Raises TagNotFoundException if no tag is found.
        """
        tag_to_delete = await self.get_tag(tag_uid, session)
        await session.delete(tag_to_delete)
        await session.commit()
        return tag_to_delete
