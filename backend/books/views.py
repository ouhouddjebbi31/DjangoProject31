from django.db.models import Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Author, Book, Genre, Review
from .permissions import IsAdminOrReadOnly, IsOwner
from .serializers import AuthorSerializer, BookSerializer, GenreSerializer, ReviewSerializer

class BookViewSet(viewsets.ModelViewSet):
	queryset = Book.objects.all().prefetch_related('authors', 'genres').annotate(
		avg_rating=Avg('reviews__rating'), rating_count=Count('reviews', distinct=True)
	)
	serializer_class = BookSerializer
	permission_classes = [IsAdminOrReadOnly]
	filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
	search_fields = ['title', 'authors__name']
	filterset_fields = ['genres', 'publication_year']
	ordering_fields = ['avg_rating', 'publication_year', 'title']
	ordering = ['title']

	@action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticatedOrReadOnly])
	def reviews(self, request, pk=None):
		book = self.get_object()
		if request.method == 'GET':
			return Response(ReviewSerializer(book.reviews.select_related('user'), many=True).data)
		serializer = ReviewSerializer(data=request.data, context={'request': request, 'book': book})
		serializer.is_valid(raise_exception=True)
		serializer.save(user=request.user, book=book)
		return Response(serializer.data, status=status.HTTP_201_CREATED)

	@action(detail=True, methods=['get'])
	def similar(self, request, pk=None):
		from recommendations.engine import similar_books
		return Response(similar_books(self.get_object()))


class AuthorViewSet(viewsets.ModelViewSet):
	queryset = Author.objects.all()
	serializer_class = AuthorSerializer
	permission_classes = [IsAdminOrReadOnly]
	filter_backends = [filters.SearchFilter]
	search_fields = ['name']


class GenreViewSet(viewsets.ModelViewSet):
	queryset = Genre.objects.all()
	serializer_class = GenreSerializer
	permission_classes = [IsAdminOrReadOnly]
	filter_backends = [filters.SearchFilter]
	search_fields = ['name']


class ReviewViewSet(viewsets.ModelViewSet):
	queryset = Review.objects.select_related('user', 'book')
	serializer_class = ReviewSerializer
	permission_classes = [IsOwner]
	http_method_names = ['patch', 'delete', 'head', 'options']
