from datetime import datetime

from sqlalchemy import Column, ForeignKey, Table, func
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    registry,
    relationship,
)

table_registry = registry()


user_collection_table = Table(
    'user_collection_table',
    table_registry.metadata,
    Column('user_id', ForeignKey('users.id'), primary_key=True),
    Column('book_id', ForeignKey('books.id'), primary_key=True),
)


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    collection: Mapped[list['Book']] = relationship(
        init=False,
        secondary=user_collection_table,
        back_populates='users',
    )
    books_created: Mapped[list['Book']] = relationship(
        init=False, back_populates='created_by', cascade='all, delete-orphan'
    )
    authors_created: Mapped[list['Author']] = relationship(
        init=False, back_populates='created_by', cascade='all, delete-orphan'
    )


@table_registry.mapped_as_dataclass
class Author:
    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    created_by_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), init=False
    )

    created_by: Mapped[User] = relationship(
        back_populates='authors_created', init=False
    )

    books: Mapped[list['Book']] = relationship(
        init=False, back_populates='author', cascade='all, delete-orphan'
    )


@table_registry.mapped_as_dataclass
class Book:
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)
    year: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
    author_id: Mapped[int] = mapped_column(
        ForeignKey('authors.id'), init=False
    )
    created_by_id: Mapped[int] = mapped_column(
        ForeignKey('users.id'), init=False
    )

    author: Mapped[Author] = relationship(back_populates='books', init=False)
    created_by: Mapped[User] = relationship(
        back_populates='books_created', init=False
    )

    users: Mapped[list['User']] = relationship(
        init=False,
        secondary=user_collection_table,
        back_populates='collection',
    )
