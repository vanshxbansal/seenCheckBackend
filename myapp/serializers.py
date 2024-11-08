from rest_framework import serializers
from .models import UserPost

class UserPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPost
        fields = ['id', 'title', 'image', 'created_at']


class EmailSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=255)
    message = serializers.CharField()
    recipient = serializers.EmailField()

