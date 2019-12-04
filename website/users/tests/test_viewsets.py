import json

from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase, override_settings, TransactionTestCase
from django.utils import timezone

from website.users.tests.utils import UserFactory

from website.users.models import OneTimeToken

from rest_framework.authtoken.models import Token

User = get_user_model()


class UserViewSetCreateTestCase(TestCase):
    """Tests for UserViewSet.create"""

    def setUp(self):
        """
        A user is created in during the migrations. Hence, there will be at least one user in the database.
        1 user in the database = none user created during the test.
        """
        self.url = '/api/v1/users/profiles/'
        self.user = UserFactory(verified=True)

    def test_create_user_with_email(self):
        """
        Test a create a user with email
        """
        data = {
            'email': 'test@example.com ',
            'username': 'some_username',
            'password': 'randompassword123?=)(/'
        }
        data = json.dumps(data, cls=DjangoJSONEncoder)
        response = self.client.post(self.url, data=data, content_type='application/json')

        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.status_code, 201)

    def test_create_user_without_email(self):
        """
        Test a create a user without email. Should not work!
         """
        data = {
            'username': 'some_username',
            'password': 'randompassword123?=)(/'
        }
        response = self.client.post(self.url, data=data)

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 400)

    def test_create_user_without_password(self):
        """
        Test a create a user without password. Should not work!
        """
        data = {
            'email': 'test@example.com ',
            'username': 'some_username',
        }
        response = self.client.post(self.url, data=data)

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.status_code, 400)


class TestUserUpdateViewSet(TestCase):

    def setUp(self):
        self.clinic = ClinicFactory()
        self.url = '/api/v1/users/profiles/'
        self.user = UserFactory(verified=True)

    def test_update_user(self):

        self.client._login(self.user)
        self.treatment_time = timezone.now()
        data = {
            'username': 'some_username',
        }

        data = json.dumps(data, cls=DjangoJSONEncoder)
        response = self.client.put(self.url + str(self.user.link_id) + '/', data=data, content_type='application/json')
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(str(response.content, encoding='utf8'), data.replace(" ", ""))


class UserRetrieve(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user.set_password('password')
        self.user.save()
        self.usertoken, self.created = Token.objects.get_or_create(user=self.user)
        self.client._login(self.user)
        self.url = f'/api/v1/users/profiles/{str(self.user.link_id)}/'

    def test_retrieve_only_yourself(self):
        expected = {
            'email': self.user.email,
            'username': self.user.username,
        }
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected, json.loads(response.content.decode()))

    def test_retrieve_other_user(self):
        other_url = f'/api/v1/users/profiles/{str(self.user2.link_id)}/'
        response = self.client.get(other_url)
        expected = {
            'email': self.user.email,
            'username': self.user.username,
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected, json.loads(response.content.decode()))


class UserLoginTestCase(TestCase):
    """Tests for .users.viewsets.CustomAuthToken"""
    def setUp(self):
        self.user = UserFactory(verified=True)
        self.user.set_password('password')
        self.user.save()
        self.url = f'/login/'

    def test_email_login(self):
        response = self.client.post(self.url, data=json.dumps({'email': self.user.email, "password": 'password'}),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 200)

    def test_login_with_wrong_password(self):
        """
        Users can have None as phone or email. Test checks that authentication response is correct.
        If worong password is typed return ['Unable to login with provided credentials.']
        """
        UserFactory()
        response = self.client.post(self.url, data=json.dumps({'email': self.user.email, "password": 'hej'}),
                                    content_type='application/json')

        data = json.loads(response.content.decode())
        expected = {
            'non_field_errors': ['Unable to login with provided credentials.']
        }
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, expected)

    def test_login_without_username(self):
        """Users should not be able to login without email or phone. All fields need to be filled"""
        response = self.client.post(self.url, data=json.dumps({'email': '', "password": 'password'}),
                                    content_type='application/json')

        data = json.loads(response.content.decode())
        expected = {
            'non_field_errors': ['Both fields needs to be filled']
        }
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, expected)


class UserViewSetExist(TestCase):
    """Test for .viewsets.UserViewSet.exists"""

    def setUp(self):
        self.user = UserFactory(verified=True)
        self.url = f'/api/v1/users/profiles/exists/'
        self.client._login(self.user)

    def test_exisitng_user_email(self):
        response = self.client.post(self.url, data=json.dumps({'email': self.user.email}),
                                    content_type='application/json')

        data = json.loads(response.content.decode())
        self.assertEqual(data, {'status': True})

    def test_not_exisitng_user_email(self):
        response = self.client.post(self.url, data=json.dumps({'email': 'hej'}),
                                    content_type='application/json')

        data = json.loads(response.content.decode())
        self.assertEqual(data, {'status': False})


class UserViewSetChangePasswordTestCase(TestCase):
    """Tests for .viewsets.UserViewSet.forgot_password"""

    def setUp(self):
        self.user = UserFactory(verified=True)
        self.client._login(self.user)
        self.url = f'/api/v1/users/profiles/change_password/'

    def test_change_password(self):
        response = self.client.put(self.url, data=json.dumps({'password': 'test', 'confirmed_password': 'test'
                                                              }), content_type='application/json')
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.user.check_password('test'))

    def test_change_password_as_unauthenticated(self):
        """A unauthenticated user should not be able to change password"""
        self.client.logout()
        response = self.client.put(self.url, data=json.dumps({'password': 'test',
                                                              'confirmed_password': 'test'
                                                              }), content_type='application/json')
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 401)
        self.assertFalse(self.user.check_password('test'))


class UserViewSetPassword(TestCase):
    """Test for .users.viewsets.UserViewSet.password"""

    def setUp(self):
        self.user = UserFactory()
        self.url = f'/api/v1/users/profiles/reset_password/'

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
    def test_recover_password(self):

        data = {
            'email': self.user.email,
        }

        response = self.client.post(self.url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_send_not_existing_email(self):
        response = self.client.post(self.url, data={'email': 'random@zerebra.com'})

        self.assertEqual(response.status_code, 200)

    def test_send_wrong_data(self):
        response = self.client.post(self.url, data={'email': 1234})
        self.assertEqual(response.status_code, 400)


class UserViewSetTokenTestCase(TransactionTestCase):
    """Tests for .users.UserViewSet.password_token."""

    def setUp(self):
        self.user = UserFactory(verified=True)
        self.token = OneTimeToken(self.user)
        self.url = '/api/v1/users/profiles/password_token/'
        self.client._login(self.user)


    def test_valid_token(self):
        """Test activate user. Default behaviour."""
        response = self.client.post(self.url, data={'token': self.token.key})

        self.assertEqual(response.status_code, 200)

    def test_invalid_token(self):
        """Test login with an invalid token. Should raise an error."""
        response = self.client.post(self.url, data={'token': 'hejhej'})
        data = json.loads(response.content.decode())
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data, {'token': ['Invalid token.']})
