from django.contrib import admin
from .models import Author, Book, Genre, Review


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
	list_display = ['name']
	search_fields = ['name']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
	list_display = ['name']
	search_fields = ['name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
	list_display = ['title', 'isbn', 'publication_year', 'created_at']
	search_fields = ['title', 'isbn', 'authors__name']
	list_filter = ['publication_year', 'genres']
	filter_horizontal = ['authors', 'genres']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	list_display = ['book', 'user', 'rating', 'created_at']
	search_fields = ['book__title', 'user__username', 'comment']
	list_filter = ['rating', 'created_at']
