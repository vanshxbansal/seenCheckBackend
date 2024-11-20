from rest_framework import serializers
from .models import *

class UserPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPost
        fields = ['id', 'title', 'image', 'created_at']


class EmailSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=255)
    message = serializers.CharField()
    recipient = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    phone_number = serializers.CharField(max_length=15)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone_number']  # You can add more fields if you want

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()  # Nested serializer for UserProfile
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'profile']  # Include other fields you want

class PartySerializer(serializers.ModelSerializer):
    class Meta:
        model = Party
        fields = ['party_name', 'party_description', 'party_location', 'party_date', 'party_time', 'user']
        read_only_fields = ['user']  