from http import HTTPStatus

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from estante_digital.models import Author, User
from estante_digital.schemas import Token
from tests.factories import AuthorFactory


def test_create_author(client: TestClient, token: Token):
    response = client.post(
        '/authors',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': 'test'},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json()['name'] == 'test'


def test_create_author_with_existing_name(
    client: TestClient, token: Token, author: Author
):
    response = client.post(
        '/authors',
        headers={'Authorization': f'Bearer {token}'},
        json={'name': author.name},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == 'Author already exists'


def test_list_should_return_5_authors(
    client: TestClient, session: Session, token: Token, user: User
):
    expected_authors = 5
    for _ in range(expected_authors):
        author = AuthorFactory()
        author.created_by = user
        session.add(author)

    session.commit()

    response = client.get(
        '/authors?name=au', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['authors']) == expected_authors


def test_read_one_author(client: TestClient, token: Token, author: Author):
    response = client.get(
        f'/authors/{author.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': author.id,
        'name': author.name,
        'books': [],
    }


def test_read_one_author_not_found(client: TestClient, token: Token):
    response = client.get(
        '/authors/2', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Author not found'
