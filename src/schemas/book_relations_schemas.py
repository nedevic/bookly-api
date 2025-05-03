from typing import List

from src.schemas.books_schemas import Book
from src.schemas.reviews_schemas import Review


class BookRelations(Book):
    reviews: List[Review]
