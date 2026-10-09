from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .engine import personalized_recommendations

class RecommendationsView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		return Response(personalized_recommendations(request.user))
