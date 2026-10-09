from rest_framework import serializers

from .models import Author, Book, Genre, Review


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'biography']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'username', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'username', 'created_at', 'updated_at']

    def validate(self, attrs):
        if self.instance is None and Review.objects.filter(user=self.context['request'].user, book=self.context['book']).exists():
            raise serializers.ValidationError('You have already reviewed this book.')
        return attrs


class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    author_ids = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), many=True, source='authors', write_only=True, required=False)
    genre_ids = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all(), many=True, source='genres', write_only=True, required=False)
    avg_rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'isbn', 'description', 'publication_year', 'cover_url', 'authors', 'genres', 'author_ids', 'genre_ids', 'avg_rating', 'rating_count', 'created_at']
        read_only_fields = ['id', 'created_at', 'avg_rating', 'rating_count']


class ReviewCreateSerializer(ReviewSerializer):
    class Meta(ReviewSerializer.Meta):
        fields = ['id', 'rating', 'comment', 'created_at', 'updated_at', 'username']
