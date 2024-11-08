from django.test import TestCase

from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
import ast
from users.models import User

class JwtTestCase(APITestCase):

    def setUp(self):
        # set url JWT
        self.url = reverse("token_obtain_pair")
        # create superuser
        self.superuser = User.objects.create_superuser(email='admin@admin.com', password="admin")
        self.superuser.save()
        # create user
        self.user = User.objects.create_user(email='user@user.com', password="user")
        self.user.save()

    def test_create_user(self):
        user = User.objects.get(email='user@user.com')
        self.assertIsNotNone(user)
        self.assertEqual(self.user, user)
        self.assertNotEqual(user.password, 'admin')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        superuser = User.objects.get( email='admin@admin.com')
        self.assertIsNotNone(superuser)
        self.assertEqual(self.superuser, superuser)
        self.assertNotEqual(superuser.password, 'admin')
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)


    def test_get_jwt(self):
        credentials = {
                'email': 'admin@admin.com',
                'password': 'admin',
            }
        response = self.client.post( self.url, credentials, format="json")
        content = ast.literal_eval(response.content.decode("UTF-8"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(content['access'])
        self.assertIsNotNone(content['refresh'])