from typing import List, Optional, Dict, Any
from models.book import BookResponse, BookSearchParams
import aiosqlite
from services.book_service import BookService
from utils.exceptions import NotFoundError


class SearchService:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def search_books(self, params: BookSearchParams) -> Dict[str, Any]:
        async with self.db.cursor() as cursor:
            # Build base query
            query = """
                SELECT DISTINCT b.id
                FROM books b
                LEFT JOIN book_authors ba ON b.id = ba.book_id
                LEFT JOIN authors a ON ba.author_id = a.id
                LEFT JOIN book_genres bg ON b.id = bg.book_id
                LEFT JOIN genres g ON bg.genre_id = g.id
                WHERE b.is_active = TRUE
            """

            conditions = []
            query_params = []

            # Add search conditions
            if params.title:
                conditions.append("b.title LIKE ?")
                query_params.append(f"%{params.title}%")
            if params.author:
                conditions.append("a.name LIKE ?")
                query_params.append(f"%{params.author}%")
            if params.genre:
                conditions.append("g.name = ?")
                query_params.append(params.genre)
            if params.year_from:
                conditions.append("b.publication_year >= ?")
                query_params.append(params.year_from)
            if params.year_to:
                conditions.append("b.publication_year <= ?")
                query_params.append(params.year_to)
            if params.isbn:
                conditions.append("b.isbn = ?")
                query_params.append(params.isbn)
            if params.available_only:
                conditions.append("b.copies_available > 0")

            if conditions:
                query += " AND " + " AND ".join(conditions)

            # Add sorting
            if params.sort_by:
                sort_field = {
                    "title": "b.title",
                    "author": "a.name",
                    "year": "b.publication_year",
                }.get(params.sort_by, "b.title")
                sort_order = "DESC" if params.sort_order == "desc" else "ASC"
                query += f" ORDER BY {sort_field} {sort_order}"

            # Count total results for pagination
            count_query = f"SELECT COUNT(*) as total FROM ({query})"
            await cursor.execute(count_query, query_params)
            total = (await cursor.fetchone())["total"]

            # Add pagination
            query += " LIMIT ? OFFSET ?"
            query_params.extend([params.per_page, (params.page - 1) * params.per_page])

            # Execute query
            await cursor.execute(query, query_params)
            book_ids = [row["id"] for row in await cursor.fetchall()]

            # Get full book details
            book_service = BookService(self.db)
            books = [await book_service.get_book_by_id(book_id) for book_id in book_ids]

            return {
                "total": total,
                "page": params.page,
                "per_page": params.per_page,
                "results": books,
            }

    async def get_genre_stats(self) -> Dict[str, int]:
        async with self.db.cursor() as cursor:
            await cursor.execute("""
                SELECT g.name, COUNT(bg.book_id) as count
                FROM genres g
                LEFT JOIN book_genres bg ON g.id = bg.genre_id
                LEFT JOIN books b ON bg.book_id = b.id AND b.is_active = TRUE
                GROUP BY g.name
                ORDER BY count DESC
            """)
            return {row["name"]: row["count"] for row in await cursor.fetchall()}

    async def get_author_stats(self) -> Dict[str, int]:
        async with self.db.cursor() as cursor:
            await cursor.execute("""
                SELECT a.name, COUNT(ba.book_id) as count
                FROM authors a
                LEFT JOIN book_authors ba ON a.id = ba.author_id
                LEFT JOIN books b ON ba.book_id = b.id AND b.is_active = TRUE
                GROUP BY a.name
                ORDER BY count DESC
            """)
            return {row["name"]: row["count"] for row in await cursor.fetchall()}