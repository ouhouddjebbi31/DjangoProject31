from rest_framework import serializers


class HistoryMessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=['user', 'assistant'])
    content = serializers.CharField(max_length=1000, allow_blank=False)


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=500, allow_blank=False, trim_whitespace=True)
    history = HistoryMessageSerializer(many=True, required=False, default=list)

    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError('Message cannot be empty.')
        return value.strip()

    def validate_history(self, value):
        if len(value) > 10:
            raise serializers.ValidationError('History cannot contain more than 10 messages.')
        return value
