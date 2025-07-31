from typing import List, Optional, Dict, Any
from models.book import BookCreate, BookUpdate, BookResponse, Author, Genre
import aiosqlite
from datetime import datetime
from utils.exceptions import NotFoundError


class BookService:
    def __init__(self, db: aiosqlite.Connection):
        self.db = db

    async def create_book(self, book_data: BookCreate) -> BookResponse:
        async with self.db.cursor() as cursor:
            # Insert book
            await cursor.execute("""
                INSERT INTO books (title, publication_year, isbn, copies_available, is_active)
                VALUES (?, ?, ?, ?, ?)
            """, (
                book_data.title,
                book_data.publication_year,
                book_data.isbn,
                book_data.copies_available,
                book_data.is_active,
            ))

            book_id = cursor.lastrowid

            # Process authors
            author_ids = []
            for author_name in book_data.authors:
                author_id = await self._get_or_create_author(author_name)
                author_ids.append(author_id)

            # Process genres
            genre_ids = []
            for genre_name in book_data.genres:
                genre_id = await self._get_or_create_genre(genre_name)
                genre_ids.append(genre_id)

            # Create book-author relationships
            for author_id in author_ids:
                await cursor.execute("""
                    INSERT INTO book_authors (book_id, author_id)
                    VALUES (?, ?)
                """, (book_id, author_id))

            # Create book-genre relationships
            for genre_id in genre_ids:
                await cursor.execute("""
                    INSERT INTO book_genres (book_id, genre_id)
                    VALUES (?, ?)
                """, (book_id, genre_id))

            await self.db.commit()

            return await self.get_book_by_id(book_id)

    async def _get_or_create_author(self, name: str) -> int:
        async with self.db.cursor() as cursor:
            await cursor.execute("""
                SELECT id FROM authors WHERE name = ?
            """, (name,))
            row = await cursor.fetchone()

            if row:
                return row["id"]
            else:
                await cursor.execute("""
                    INSERT INTO authors (name) VALUES (?)
                """, (name,))
                return cursor.lastrowid

    async def _get_or_create_genre(self, name: str) -> int:
        async with self.db.cursor() as cursor:
            await cursor.execute("""
                SELECT id FROM genres WHERE name = ?
            """, (name,))
            row = await cursor.fetchone()

            if row:
                return row["id"]
            else:
                await cursor.execute("""
                    INSERT INTO genres (name) VALUES (?)
                """, (name,))
                return cursor.lastrowid

    async def get_book_by_id(self, book_id: int) -> BookResponse:
        async with self.db.cursor() as cursor:
            await cursor.execute("""
                SELECT * FROM books WHERE id = ?
            """, (book_id,))
            book_row = await cursor.fetchone()

            if not book_row:
                raise NotFoundError(f"Book with id {book_id} not found")

            # Get authors
            await cursor.execute("""
                SELECT a.id, a.name 
                FROM authors a
                JOIN book_authors ba ON a.id = ba.author_id
                WHERE ba.book_id = ?
            """, (book_id,))
            author_rows = await cursor.fetchall()
            authors = [Author(id=row["id"], name=row["name"]) for row in author_rows]

            # Get genres
            await cursor.execute("""
                SELECT g.id, g.name 
                FROM genres g
                JOIN book_genres bg ON g.id = bg.genre_id
                WHERE bg.book_id = ?
            """, (book_id,))
            genre_rows = await cursor.fetchall()
            genres = [Genre(id=row["id"], name=row["name"]) for row in genre_rows]

            return BookResponse(
                id=book_row["id"],
                title=book_row["title"],
                authors=authors,
                genres=genres,
                publication_year=book_row["publication_year"],
                isbn=book_row["isbn"],
                copies_available=book_row["copies_available"],
                is_active=book_row["is_active"],
                created_at=book_row["created_at"],
                updated_at=book_row["updated_at"],
            )

    async def update_book(self, book_id: int, book_data: BookUpdate) -> BookResponse:
        async with self.db.cursor() as cursor:
            # Check if book exists
            await cursor.execute("SELECT id FROM books WHERE id = ?", (book_id,))
            if not await cursor.fetchone():
                raise NotFoundError(f"Book with id {book_id} not found")

            # Build update query
            updates = []
            params = []
            if book_data.title is not None:
                updates.append("title = ?")
                params.append(book_data.title)
            if book_data.publication_year is not None:
                updates.append("publication_year = ?")
                params.append(book_data.publication_year)
            if book_data.isbn is not None:
                updates.append("isbn = ?")
                params.append(book_data.isbn)
            if book_data.copies_available is not None:
                updates.append("copies_available = ?")
                params.append(book_data.copies_available)
            if book_data.is_active is not None:
                updates.append("is_active = ?")
                params.append(book_data.is_active)

            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                query = f"UPDATE books SET {', '.join(updates)} WHERE id = ?"
                params.append(book_id)
                await cursor.execute(query, params)

            # Update authors if provided
            if book_data.authors is not None:
                await cursor.execute("DELETE FROM book_authors WHERE book_id = ?", (book_id,))
                for author_name in book_data.authors:
                    author_id = await self._get_or_create_author(author_name)
                    await cursor.execute("""
                        INSERT INTO book_authors (book_id, author_id)
                        VALUES (?, ?)
                    """, (book_id, author_id))

            # Update genres if provided
            if book_data.genres is not None:
                await cursor.execute("DELETE FROM book_genres WHERE book_id = ?", (book_id,))
                for genre_name in book_data.genres:
                    genre_id = await self._get_or_create_genre(genre_name)
                    await cursor.execute("""
                        INSERT INTO book_genres (book_id, genre_id)
                        VALUES (?, ?)
                    """, (book_id, genre_id))

            await self.db.commit()
            return await self.get_book_by_id(book_id)

    async def delete_book(self, book_id: int, soft_delete: bool = True) -> None:
        async with self.db.cursor() as cursor:
            if soft_delete:
                await cursor.execute("""
                    UPDATE books SET is_active = FALSE WHERE id = ?
                """, (book_id,))
            else:
                await cursor.execute("DELETE FROM books WHERE id = ?", (book_id,))
            await self.db.commit()

    async def list_books(self, page: int = 1, per_page: int = 10) -> List[BookResponse]:
        async with self.db.cursor() as cursor:
            offset = (page - 1) * per_page
            await cursor.execute("""
                SELECT id FROM books 
                WHERE is_active = TRUE
                ORDER BY title
                LIMIT ? OFFSET ?
            """, (per_page, offset))
            book_ids = [row["id"] for row in await cursor.fetchall()]
            return [await self.get_book_by_id(book_id) for book_id in book_ids]