from http import HTTPStatus

from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session

from estante_digital.models import User
from estante_digital.schemas import Token
from tests.factories import AuthorFactory, BookFactory


def test_root_deve_retornar_ok_e_ola_mundo(client: TestClient):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Olá Mundo!'}


def test_book_and_author_created_by_a_user(
    client: TestClient, session: Session, user: User, token: Token
):
    author = AuthorFactory()
    author.created_by = user

    book = BookFactory()
    book.created_by = user
    book.author = author

    session.add_all([author, book])
    session.commit()

    assert author.created_by == user
    assert author in user.authors_created
    assert book.created_by == user
    assert book in user.books_created

    response = client.get(
        f'/books/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    response = response.json()

    assert response['id'] == book.id
    assert response['title'] == book.title
    assert response['author'] == {'id': author.id, 'name': author.name}
