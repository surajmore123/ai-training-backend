from rest_framework import serializers
from .models import MeetingTranscript

class MeetingTranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingTranscript
        fields = ["id", "title", "content", "created_at"]
