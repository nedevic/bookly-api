from typing import List

from src.schemas.auth_schemas import User
from src.schemas.books_schemas import Book
from src.schemas.reviews_schemas import Review


class UserRelations(User):
    books: List[Book]
    reviews: List[Review]
