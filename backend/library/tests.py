from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from books.models import Book
from .models import ReadingList


class ReadingListPrivacyTests(APITestCase):
	def setUp(self):
		self.user_a = User.objects.create_user(username='a', password='StrongPass123!')
		self.user_b = User.objects.create_user(username='b', password='StrongPass123!')
		self.book = Book.objects.create(title='Private Book', description='Description')
		self.entry = ReadingList.objects.create(user=self.user_b, book=self.book)

	def test_user_sees_only_own_entries(self):
		self.client.force_authenticate(self.user_a)
		response = self.client.get('/api/reading-list/')
		self.assertEqual(response.data['count'], 0)
		self.assertEqual(self.client.patch(f'/api/reading-list/{self.entry.id}/', {'is_favorite': True}).status_code, 404)
