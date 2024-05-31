from pydantic import BaseModel, ConfigDict, EmailStr

from estante_digital.utils import sanitize_input


# message
class Message(BaseModel):
    message: str


# token
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


# helper book and author
class AuthorPublicWithoutBooks(BaseModel):
    id: int
    name: str


class BookPublicWithoutAuthor(BaseModel):
    id: int
    title: str
    year: int


# author
class AuthorSchema(BaseModel):
    name: str

    def __init__(self, **kwargs: ConfigDict):
        super().__init__(**kwargs)
        self.name = sanitize_input(self.name)


class AuthorPublic(BaseModel):
    id: int
    name: str
    books: list[BookPublicWithoutAuthor]
    model_config = ConfigDict(from_attributes=True)


class AuthorList(BaseModel):
    authors: list[AuthorPublicWithoutBooks]


# book
class BookSchema(BaseModel):
    title: str
    year: int
    author_id: int

    def __init__(self, **kwargs: ConfigDict):
        super().__init__(**kwargs)
        self.title = sanitize_input(self.title)


class BookPublic(BaseModel):
    id: int
    title: str
    year: int
    author: AuthorPublicWithoutBooks
    model_config = ConfigDict(from_attributes=True)


class BookList(BaseModel):
    books: list[BookPublic]


# user
class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str

    def __init__(self, **kwargs: ConfigDict):
        super().__init__(**kwargs)
        self.username = sanitize_input(self.username)
        self.email = sanitize_input(self.email)


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    collection: list[BookPublic]
    model_config = ConfigDict(from_attributes=True)


class UserCollection(BaseModel):
    collection: list[BookPublic]
