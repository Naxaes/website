import factory

from website.users.models import User


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User
        django_get_or_create = ('username', )

    email = factory.Sequence(lambda n: 'email{0}@example.com'.format(n))
    username = factory.Sequence(lambda n: 'username{0}'.format(n))
    password = 'supersafepassword'
