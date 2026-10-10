import logging
import time

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .llm import ChatBusy, ChatNotConfigured, ChatUnavailable, generate_reply
from .prompts import build_messages
from .retrieval import retrieve_context
from .serializers import ChatRequestSerializer
from .throttles import ChatRateThrottle

logger = logging.getLogger(__name__)


class ChatView(APIView):
	permission_classes = [IsAuthenticated]
	throttle_classes = [ChatRateThrottle]

	def post(self, request):
		serializer = ChatRequestSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		started = time.monotonic()
		context = retrieve_context(serializer.validated_data['message'], request.user)
		system_prompt, messages = build_messages(context['text'], serializer.validated_data['history'], serializer.validated_data['message'])
		try:
			reply = generate_reply(system_prompt, messages)
		except ChatNotConfigured:
			logger.warning('Chat unavailable user=%s reason=not_configured', request.user.pk)
			return Response({'error': "The assistant isn't configured yet."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
		except ChatBusy:
			logger.warning('Chat unavailable user=%s reason=provider_rate_limit', request.user.pk)
			return Response({'error': 'The assistant is busy right now. Please try again shortly.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
		except ChatUnavailable:
			logger.warning('Chat unavailable user=%s reason=provider_unavailable', request.user.pk)
			return Response({'error': 'The assistant is temporarily unavailable. Please try again later.'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
		sources = [{'id': book['id'], 'title': book['title'], 'authors': book['authors'], 'cover_url': book['cover_url']} for book in context['books']]
		logger.info('Chat completed user=%s latency_ms=%d sources=%d', request.user.pk, round((time.monotonic() - started) * 1000), len(sources))
		return Response({'reply': reply, 'sources': sources})
