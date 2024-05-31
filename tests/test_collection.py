from http import HTTPStatus

from fastapi.testclient import TestClient

from estante_digital.models import Book, User
from estante_digital.schemas import Token


def test_read_collection(
    client: TestClient,
    token: Token,
    user_with_collection: User,
    book: Book,
):
    response = client.get(
        '/collection', headers={'Authorization': f'Bearer {token}'}
    )

    resp = response.json()

    assert response.status_code == HTTPStatus.OK
    assert len(resp['collection']) == 1
    assert resp['collection'][0]['title'] == book.title
    assert resp['collection'][0]['author'] == {
        'id': book.author.id,
        'name': book.author.name,
    }


def test_add_book_to_collection(client: TestClient, token: Token, book: Book):
    response = client.post(
        f'/collection/add/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    resp = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp['message'] == f'Book {book.title} added to collection'


def test_add_book_already_on_collection(
    client: TestClient,
    token: Token,
    user_with_collection: User,
    book: Book,
):
    response = client.post(
        f'/collection/add/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == 'Book already on collection'


def test_add_unexisted_book_to_collection(client: TestClient, token: Token):
    response = client.post(
        '/collection/add/2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Book not found'


def test_remove_book_to_collection(
    client: TestClient,
    token: Token,
    user_with_collection: User,
    book: Book,
):
    response = client.delete(
        f'/collection/remove/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    resp = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp['message'] == f'Book {book.title} removed from collection'


def test_remove_unexisted_book_from_collection(
    client: TestClient, token: Token
):
    response = client.delete(
        '/collection/remove/2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Book not found'


def test_remove_book_not_on_collection(
    client: TestClient, token: Token, book: Book
):
    response = client.delete(
        f'/collection/remove/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Book not in collection'


def test_combined_actions_on_collection(
    client: TestClient, token: Token, book: Book
):
    response = client.post(
        f'/collection/add/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    r = response.json()
    assert response.status_code == HTTPStatus.OK
    assert r['message'] == f'Book {book.title} added to collection'

    response = client.get(
        '/collection', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['collection']) == 1

    response = client.delete(
        f'/collection/remove/{book.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    r = response.json()
    assert response.status_code == HTTPStatus.OK
    assert r['message'] == f'Book {book.title} removed from collection'
