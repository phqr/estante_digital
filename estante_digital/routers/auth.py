from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from estante_digital.database import get_session
from estante_digital.models import User
from estante_digital.schemas import Token
from estante_digital.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
Session_ = Annotated[Session, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter()


@router.post('/token', response_model=Token)
def login_for_access_token(
    form_data: OAuth2Form,
    session: Session_,
):
    user = session.scalar(
        select(User).where(
            (User.username == form_data.username)
            | (User.email == form_data.username)
        )
    )

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Incorrect email or password',
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data={'sub': user.email})

    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/refresh_token', response_model=Token)
def refresh_access_token(user: CurrentUser):
    new_access_token = create_access_token(data={'sub': user.email})

    return {'access_token': new_access_token, 'token_type': 'bearer'}
