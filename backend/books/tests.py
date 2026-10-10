from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Book, Review


class BookApiTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='reader', password='StrongPass123!')
		self.staff = User.objects.create_user(username='staff', password='StrongPass123!', is_staff=True)
		self.book = Book.objects.create(title='Test Book', description='A useful description')
		self.other = Book.objects.create(title='Other Book', description='Another description')

	def test_anonymous_can_read_but_not_create_books(self):
		self.assertEqual(self.client.get('/api/books/').status_code, status.HTTP_200_OK)
		self.assertEqual(self.client.post('/api/books/', {'title': 'Nope', 'description': 'Nope'}).status_code, status.HTTP_401_UNAUTHORIZED)

	def test_staff_can_create_books(self):
		self.client.force_authenticate(self.staff)
		response = self.client.post('/api/books/', {'title': 'Staff Book', 'description': 'Created by staff'})
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_average_rating_is_annotated(self):
		Review.objects.create(user=self.user, book=self.book, rating=5)
		response = self.client.get(f'/api/books/{self.book.id}/')
		self.assertEqual(response.data['avg_rating'], 5.0)
		self.assertEqual(response.data['rating_count'], 1)

	def test_user_can_review_once(self):
		self.client.force_authenticate(self.user)
		payload = {'rating': 4, 'comment': 'Good'}
		self.assertEqual(self.client.post(f'/api/books/{self.book.id}/reviews/', payload).status_code, 201)
		self.assertEqual(self.client.post(f'/api/books/{self.book.id}/reviews/', payload).status_code, 400)

	def test_recommendations_exclude_reviewed_books(self):
		Review.objects.create(user=self.user, book=self.book, rating=5)
		self.client.force_authenticate(self.user)
		response = self.client.get('/api/recommendations/')
		self.assertNotIn(self.book.id, [item['id'] for item in response.data])
