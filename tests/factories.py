import factory

from estante_digital.models import Author, Book, User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')


class AuthorFactory(factory.Factory):
    class Meta:
        model = Author

    name = factory.Sequence(lambda n: f'author{n}')


class BookFactory(factory.Factory):
    class Meta:
        model = Book

    title = factory.Sequence(lambda n: f'book{n}')
    year = 2024
