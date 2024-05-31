from http import HTTPStatus

from fastapi.testclient import TestClient

from estante_digital.models import User
from estante_digital.schemas import Token, UserPublic


def test_create_user(client: TestClient):
    response = client.post(
        '/user',
        json={
            'username': 'test',
            'email': 'test@test.com',
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert 'id' in response.json().keys()


def test_create_user_with_taken_username(client: TestClient, user: User):
    response = client.post(
        '/user',
        json={
            'username': user.username,
            'email': 'test@test.com',
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == 'Username already exists'


def test_create_user_with_taken_email(client: TestClient, user: User):
    response = client.post(
        '/user',
        json={
            'username': 'test',
            'email': user.email,
            'password': '123456',
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == 'Email already exists'


def test_read_user(client: TestClient, user: User, token: Token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        f'/user/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.json() == user_schema


def test_read_user_with_wrong_id(
    client: TestClient, other_user: User, token: Token
):
    response = client.get(
        f'/user/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == 'Not enough permissions'


def test_update_user(client: TestClient, user: User, token: Token):
    response = client.put(
        f'/user/{user.id}',
        json={
            'username': 'test1',
            'email': 'test@test.com',
            'password': '123456',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['username'] == 'test1'


def test_update_user_with_wrong_id(
    client: TestClient, other_user: User, token: Token
):
    response = client.put(
        f'/user/{other_user.id}',
        json={
            'username': 'test',
            'email': 'test@test.com',
            'password': '123456',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == 'Not enough permissions'


def test_update_user_with_taken_username(
    client: TestClient, user: User, other_user: User, token: Token
):
    response = client.put(
        f'/user/{user.id}',
        json={
            'username': other_user.username,
            'email': 'test@test.com',
            'password': '123456',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == 'Username already exists'


def test_update_user_with_taken_email(
    client: TestClient, user: User, other_user: User, token: Token
):
    response = client.put(
        f'/user/{user.id}',
        json={
            'username': 'test1',
            'email': other_user.email,
            'password': '123456',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == 'Email already exists'


def test_update_user_with_invalid_email(
    client: TestClient, user: User, token: Token
):
    response = client.put(
        f'/user/{user.id}',
        json={
            'username': 'test1',
            'email': 'testtest.com',
            'password': '123456',
        },
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_delete_user(client: TestClient, user: User, token: Token):
    response = client.delete(
        f'/user/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['message'] == 'User deleted'


def test_delete_user_with_wrong_id(
    client: TestClient, other_user: User, token: Token
):
    response = client.delete(
        f'/user/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == 'Not enough permissions'
