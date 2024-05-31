from http import HTTPStatus

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from estante_digital.models import Author, Book, User
from estante_digital.schemas import Token
from tests.factories import AuthorFactory, BookFactory


def test_create_book(client: TestClient, token: Token, author: Author):
    response = client.post(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'test', 'year': 2024, 'author_id': author.id},
    )

    resp = response.json()

    assert response.status_code == HTTPStatus.CREATED
    assert resp['title'] == 'test'
    assert resp['author'] == {'id': author.id, 'name': author.name}


def test_create_book_with_unexisted_author(client: TestClient, token: Token):
    response = client.post(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'test', 'year': 2024, 'author_id': 2},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Author not found'


def test_create_book_with_existing_name(
    client: TestClient, token: Token, book: Book, author: Author
):
    response = client.post(
        '/books',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': book.title, 'year': 2024, 'author_id': author.id},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == 'Book already exists'


def test_search_by_title_list_should_return_5_books(
    client: TestClient,
    token: Token,
    session: Session,
    author: Author,
    user: User,
):
    expected_books = 5
    for _ in range(expected_books):
        book = BookFactory()
        book.author = author
        book.created_by = user
        session.add(book)

    session.commit()

    response = client.get(
        '/books?title=bo', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['books']) == expected_books


def test_search_by_year_list_should_return_5_books(
    client: TestClient,
    token: Token,
    session: Session,
    author: Author,
    user: User,
):
    expected_books = 5
    for _ in range(expected_books):
        book = BookFactory()
        book.author = author
        book.created_by = user
        session.add(book)

    session.commit()

    response = client.get(
        '/books?year=2024', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['books']) == expected_books


def test_search_by_author_id_list_should_return_5_books(
    client: TestClient,
    token: Token,
    session: Session,
    author: Author,
    user: User,
):
    expected_books = 5
    for _ in range(expected_books):
        book = BookFactory()
        book.author = author
        book.created_by = user
        session.add(book)

    session.commit()

    response = client.get(
        f'/books?author_id={author.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['books']) == expected_books


def test_combined_search_list_should_return_5_books(
    client: TestClient,
    session: Session,
    token: Token,
    author: Author,
    user: User,
):
    other_author = AuthorFactory()
    other_author.created_by = user
    session.add(other_author)

    expected_books = 5
    for _ in range(expected_books):
        book = BookFactory()
        book.author = author
        book.created_by = user
        session.add(book)

    for _ in range(3):
        book = BookFactory()
        book.author = other_author
        book.created_by = user
        session.add(book)

    session.commit()

    response = client.get(
        f'/books?author_id={author.id}&year=2024&title=boo',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['books']) == expected_books


def test_get_one_book(client: TestClient, token: Token, book: Book):
    response = client.get(
        f'/books/{book.id}', headers={'Authorization': f'Bearer {token}'}
    )

    resp = response.json()

    assert response.status_code == HTTPStatus.OK
    assert resp['title'] == book.title
    assert resp['author'] == {'id': book.author.id, 'name': book.author.name}


def test_get_one_book_not_found(client: TestClient, token: Token):
    response = client.get(
        '/books/2', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()['detail'] == 'Book not found'
