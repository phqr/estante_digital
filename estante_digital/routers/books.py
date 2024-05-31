from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from estante_digital.database import get_session
from estante_digital.models import Author, Book, User
from estante_digital.schemas import BookList, BookPublic, BookSchema
from estante_digital.security import get_current_user

router = APIRouter()

Session_ = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=BookPublic)
def create_book(
    book: BookSchema, session: Session_, current_user: CurrentUser
):
    """
    cria um livro
    não será ligado a um usuário (vai aparecer pra todos)
    o usuario deve estar logado
    schema de retorno: id, title, {author.id, author.name}
    """
    db_book = session.scalar(select(Book).where(Book.title == book.title))
    if db_book:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Book already exists'
        )

    db_author = session.scalar(
        select(Author).where(Author.id == book.author_id)
    )
    if not db_author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Author not found'
        )

    db_book = Book(title=book.title, year=book.year)
    db_book.created_by = current_user
    db_book.author = db_author

    session.add(db_book)
    session.commit()
    session.refresh(db_book)

    return db_book


@router.get('/', status_code=HTTPStatus.OK, response_model=BookList)
def get_books(  # noqa
    session: Session_,
    current_user: CurrentUser,
    # author_name: str = Query(None),
    author_id: int = Query(None),
    title: str = Query(None),
    year: int = Query(None),
    offset: int = Query(None),
    limit: int = Query(None),
):
    """
    retorna uma lista de livros
    recebe query parameters '/book?name=xxxx&year=xxxx'
    paginado
    o usuario deve estar logado
    schema de retorno: id, name, {author.id, author.name}
    """
    query = select(Book)

    if title:
        query = query.filter(Book.title.contains(title))

    if year:
        query = query.filter(Book.year == year)

    if author_id:
        query = query.filter(Book.author_id == author_id)

    books = session.scalars(query.offset(offset).limit(limit)).all()

    return {'books': books}


@router.get('/{book_id}', status_code=HTTPStatus.OK, response_model=BookPublic)
def get_book(book_id: int, session: Session_, current_user: CurrentUser):
    """
    retorna os dados de um livro
    o usuario deve estar logado
    schema de retorno: id, name, {author.id, author.name}
    """
    book = session.scalar(select(Book).where(Book.id == book_id))
    if not book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Book not found'
        )

    return book
