from fastapi import FastAPI

from estante_digital.routers import auth, authors, books, collection, users

app = FastAPI()
app.include_router(users.router, prefix='/user', tags=['users'])
app.include_router(auth.router, prefix='/auth', tags=['auth'])
app.include_router(authors.router, prefix='/authors', tags=['authors'])
app.include_router(books.router, prefix='/books', tags=['books'])
app.include_router(
    collection.router, prefix='/collection', tags=['collection']
)


@app.get('/')
def read_root():
    return {'message': 'Olá Mundo!'}
