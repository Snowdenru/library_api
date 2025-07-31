from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class Author(BaseModel):
    id: int
    name: str


class Genre(BaseModel):
    id: int
    name: str


class BookCreate(BaseModel):
    title: str
    authors: List[str]
    genres: List[str] = []
    publication_year: int
    isbn: Optional[str] = None
    copies_available: int = 1
    is_active: bool = True


class BookUpdate(BaseModel):
    title: Optional[str] = None
    authors: Optional[List[str]] = None
    genres: Optional[List[str]] = None
    publication_year: Optional[int] = None
    isbn: Optional[str] = None
    copies_available: Optional[int] = None
    is_active: Optional[bool] = None


from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class BookResponse(BaseModel):
    id: int
    title: str
    authors: List[Author]
    genres: List[Genre]
    publication_year: int
    isbn: Optional[str]
    copies_available: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        # Конвертируем datetime в строку
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data

class BookSearchParams(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    isbn: Optional[str] = None
    available_only: bool = False
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"
    page: int = 1
    per_page: int = 10