from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class UserApiTests(APITestCase):
	def test_register_creates_user_and_profile(self):
		response = self.client.post('/api/auth/register/', {
			'username': 'new_reader',
			'email': 'reader@example.com',
			'password': 'A-strong-password-123!',
		})
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(User.objects.get(username='new_reader').profile)

	def test_jwt_login_and_me_endpoint(self):
		User.objects.create_user(username='reader', password='A-strong-password-123!')
		token = self.client.post('/api/auth/token/', {'username': 'reader', 'password': 'A-strong-password-123!'})
		self.assertEqual(token.status_code, status.HTTP_200_OK)
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.data['access']}")
		response = self.client.get('/api/me/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['username'], 'reader')

	def test_superuser_can_open_admin(self):
		admin = User.objects.create_superuser(username='admin', email='admin@example.com', password='A-strong-password-123!')
		self.client.force_login(admin)
		response = self.client.get('/admin/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
