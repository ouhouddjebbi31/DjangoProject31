from django.contrib import admin
from .models import ReadingList


@admin.register(ReadingList)
class ReadingListAdmin(admin.ModelAdmin):
	list_display = ['user', 'book', 'status', 'is_favorite', 'added_at']
	search_fields = ['user__username', 'book__title']
	list_filter = ['status', 'is_favorite']
