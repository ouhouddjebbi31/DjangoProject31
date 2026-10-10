from rest_framework import serializers

from books.serializers import BookSerializer
from .models import ReadingList


class ReadingListSerializer(serializers.ModelSerializer):
    book_detail = BookSerializer(source='book', read_only=True)

    class Meta:
        model = ReadingList
        fields = ['id', 'book', 'book_detail', 'status', 'is_favorite', 'added_at']
        read_only_fields = ['id', 'book_detail', 'added_at']

    def create(self, validated_data):
        return ReadingList.objects.create(user=self.context['request'].user, **validated_data)
