from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import ReadingList
from .serializers import ReadingListSerializer

class ReadingListViewSet(viewsets.ModelViewSet):
	serializer_class = ReadingListSerializer
	permission_classes = [IsAuthenticated]
	http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

	def get_queryset(self):
		return ReadingList.objects.filter(user=self.request.user).select_related('book').prefetch_related('book__authors', 'book__genres')
