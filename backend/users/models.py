from django.db import models
from django.contrib.auth.models import User
from books.models import Genre

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	favorite_genres = models.ManyToManyField(Genre, blank=True, related_name='favorite_by')
	bio = models.TextField(blank=True)

	def __str__(self):
		return f'{self.user.username} profile'
