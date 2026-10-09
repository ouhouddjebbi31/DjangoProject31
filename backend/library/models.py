from django.db import models
from django.contrib.auth.models import User
from books.models import Book

class ReadingList(models.Model):
	WANT_TO_READ = 'WANT_TO_READ'
	READING = 'READING'
	READ = 'READ'
	STATUS_CHOICES = [(WANT_TO_READ, 'Want to read'), (READING, 'Reading'), (READ, 'Read')]

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reading_list')
	book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reading_list_entries')
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=WANT_TO_READ)
	is_favorite = models.BooleanField(default=False)
	added_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		constraints = [models.UniqueConstraint(fields=['user', 'book'], name='one_library_entry_per_user_book')]
		ordering = ['-added_at']
