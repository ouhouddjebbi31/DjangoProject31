from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

class Author(models.Model):
	name = models.CharField(max_length=255, unique=True)
	biography = models.TextField(blank=True)

	def __str__(self):
		return self.name


class Genre(models.Model):
	name = models.CharField(max_length=100, unique=True)

	def __str__(self):
		return self.name


class Book(models.Model):
	title = models.CharField(max_length=500, db_index=True)
	isbn = models.CharField(max_length=32, unique=True, null=True, blank=True)
	description = models.TextField()
	publication_year = models.PositiveIntegerField(null=True, blank=True, db_index=True)
	cover_url = models.URLField(blank=True)
	authors = models.ManyToManyField(Author, related_name='books')
	genres = models.ManyToManyField(Genre, related_name='books')
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title


class Review(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
	book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
	rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
	comment = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		constraints = [models.UniqueConstraint(fields=['user', 'book'], name='one_review_per_user_book')]
		ordering = ['-created_at']
