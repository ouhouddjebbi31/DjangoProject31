from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from books.models import Author, Book, Genre
from .llm import ChatBusy, ChatNotConfigured
from .retrieval import retrieve_context


class ChatApiTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='chat_reader', password='StrongPass123!')
		author = Author.objects.create(name='Octavia Butler')
		genre = Genre.objects.create(name='Science Fiction')
		self.book = Book.objects.create(title='Kindred', description='A time travel novel about history and memory.')
		self.book.authors.add(author)
		self.book.genres.add(genre)

	def test_anonymous_is_rejected(self):
		response = self.client.post('/api/chat/', {'message': 'Recommend a book'})
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_validation_rejects_empty_message_and_long_history(self):
		self.client.force_authenticate(self.user)
		self.assertEqual(self.client.post('/api/chat/', {'message': ' '}, format='json').status_code, status.HTTP_400_BAD_REQUEST)
		second_user = User.objects.create_user(username='validation_reader', password='StrongPass123!')
		self.client.force_authenticate(second_user)
		history = [{'role': 'user', 'content': 'hello'}] * 11
		self.assertEqual(self.client.post('/api/chat/', {'message': 'hello', 'history': history}, format='json').status_code, status.HTTP_400_BAD_REQUEST)

	def test_retrieval_finds_title_and_author(self):
		by_title = retrieve_context('Tell me about Kindred', self.user)
		by_author = retrieve_context('Books by Octavia Butler', self.user)
		self.assertEqual(by_title['books'][0]['title'], 'Kindred')
		self.assertIn('Octavia Butler', by_author['authors'])

	@patch('chat.views.generate_reply', return_value='A grounded answer.')
	def test_response_contains_reply_and_sources(self, generate_reply):
		self.client.force_authenticate(self.user)
		response = self.client.post('/api/chat/', {'message': 'Tell me about Kindred'})
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['reply'], 'A grounded answer.')
		self.assertEqual(response.data['sources'][0]['title'], 'Kindred')
		generate_reply.assert_called_once()

	@override_settings(CHAT_RATE_LIMIT='1/hour')
	@patch('chat.views.generate_reply', return_value='One answer.')
	def test_throttle_returns_429(self, generate_reply):
		self.client.force_authenticate(self.user)
		self.assertEqual(self.client.post('/api/chat/', {'message': 'First'}).status_code, status.HTTP_200_OK)
		response = self.client.post('/api/chat/', {'message': 'Second'})
		self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

	@patch('chat.views.generate_reply', side_effect=ChatNotConfigured)
	def test_missing_key_returns_friendly_503(self, generate_reply):
		self.client.force_authenticate(self.user)
		response = self.client.post('/api/chat/', {'message': 'Hello'})
		self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
		self.assertIn("isn't configured", response.data['error'])

	@patch('chat.views.generate_reply', side_effect=ChatBusy)
	def test_provider_rate_limit_returns_friendly_429(self, generate_reply):
		self.client.force_authenticate(self.user)
		response = self.client.post('/api/chat/', {'message': 'Hello'})
		self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
		self.assertIn('busy', response.data['error'])
