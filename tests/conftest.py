import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session

from estante_digital.app import app
from estante_digital.database import get_session
from estante_digital.models import table_registry
from estante_digital.security import get_password_hash
from tests.factories import AuthorFactory, BookFactory, UserFactory


@pytest.fixture()
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture()
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture()
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )
    return response.json()['access_token']


@pytest.fixture()
def user(session):
    password = 'testtest'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = password

    return user


@pytest.fixture()
def other_user(session):
    password = 'testtest'
    user = UserFactory(password=get_password_hash(password))

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = 'testtest'

    return user


@pytest.fixture()
def author(session, user):
    author = AuthorFactory()
    author.created_by = user

    session.add(author)
    session.commit()
    session.refresh(author)

    return author


@pytest.fixture()
def book(session, user, author):
    book = BookFactory()
    book.created_by = user
    book.author = author

    session.add(book)
    session.commit()
    session.refresh(book)

    return book


@pytest.fixture()
def user_with_collection(session, user, book):
    user.collection.append(book)
    session.commit()
    session.refresh(user)

    return user
