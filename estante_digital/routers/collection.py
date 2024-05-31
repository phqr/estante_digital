from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from estante_digital.database import get_session
from estante_digital.models import Book, User
from estante_digital.schemas import Message, UserCollection
from estante_digital.security import get_current_user

router = APIRouter()

Session_ = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get('/', status_code=HTTPStatus.OK, response_model=UserCollection)
def get_my_collection(current_user: CurrentUser):
    """
    retorna todos os livros da colecao do usuario
    o usuario deve estar logado
    schema de retorno: id, name, {author.id, author.name}
    """
    books = current_user.collection

    return {'collection': books}


@router.post(
    '/add/{book_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
)
def add_to_collection(
    book_id: int, session: Session_, current_user: CurrentUser
):
    """
    aciciona um livro à colecao do usuario
    o usuario deve estar logado
    """
    book = session.scalar(select(Book).where(Book.id == book_id))

    if not book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Book not found'
        )

    if book in current_user.collection:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Book already on collection',
        )

    current_user.collection.append(book)
    session.commit()
    return {'message': f'Book {book.title} added to collection'}


@router.delete(
    '/remove/{book_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
)
def remove_to_collection(
    book_id: int, session: Session_, current_user: CurrentUser
):
    """
    remove um livro da colecao do usuario
    o usuario deve estar logado
    """
    book = session.scalar(select(Book).where(Book.id == book_id))

    if not book:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Book not found'
        )

    if book not in current_user.collection:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Book not in collection',
        )

    current_user.collection.remove(book)
    session.commit()
    return {'message': f'Book {book.title} removed from collection'}
