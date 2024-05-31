from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from estante_digital.database import get_session
from estante_digital.models import Author, User
from estante_digital.schemas import AuthorList, AuthorPublic, AuthorSchema
from estante_digital.security import get_current_user

router = APIRouter()

Session_ = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', status_code=HTTPStatus.CREATED, response_model=AuthorPublic)
def create_author(
    author: AuthorSchema, session: Session_, current_user: CurrentUser
):
    """
    cria um autor
    não será ligado a um usuário (vai aparecer pra todos)
    o usuario deve estar logado
    schema de retorno: id, name, books
    """
    db_author = session.scalar(
        select(Author).where(Author.name == author.name)
    )
    if db_author:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Author already exists',
        )

    db_author = Author(name=author.name)
    db_author.created_by = current_user

    session.add(db_author)
    session.commit()

    return db_author


@router.get('/', status_code=HTTPStatus.OK, response_model=AuthorList)
def get_authors(
    session: Session_,
    current_user: CurrentUser,
    name: str = Query(None),
    offset: int = Query(None),
    limit: int = Query(None),
):
    """
    retorna uma lista de autores
    recebe query parameters '/author?name=xxxx'
    paginado
    o usuario deve estar logado
    schema de retorno: id, name
    """
    query = select(Author)

    if name:
        query = query.filter(Author.name.contains(name))

    authors = session.scalars(query.offset(offset).limit(limit)).all()

    return {'authors': authors}


@router.get(
    '/{author_id}', status_code=HTTPStatus.OK, response_model=AuthorPublic
)
def get_author(author_id: int, session: Session_, current_user: CurrentUser):
    """
    retorna os dados de um autor
    o usuario deve estar logado
    schema de retorno: id, name, books
    """
    author = session.scalar(select(Author).where(Author.id == author_id))

    if not author:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Author not found',
        )

    return author
