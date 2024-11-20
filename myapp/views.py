from rest_framework import generics, status, serializers
from rest_framework.response import Response
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import UserPost, UserOTP ,UserProfile
from .serializers import *
import os
import random
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta







class GetUserDataView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        email = request.query_params.get('email')  # Fetch the email from query params

        if not email:
            return Response({"error": "Email parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the user by email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the user data and return it
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)











class UserPostCreate(generics.CreateAPIView):
    queryset = UserPost.objects.all()
    serializer_class = UserPostSerializer

from rest_framework import generics, status
from rest_framework.response import Response
    

class SendEmailView(generics.CreateAPIView):
    serializer_class = EmailSerializer

    def create(self, request, *args, **kwargs):
        # Parse and validate the request data using the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        recipient = serializer.validated_data['recipient']
        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']
        phone_number = serializer.validated_data['phone_number']

        # Attempt to get the user by email; create if not exists
        user, created = User.objects.get_or_create(
            email=recipient,
            defaults={
                'username': recipient,
                'first_name': first_name,
                'last_name': last_name
            }
        )

        # If the user exists but was not newly created, update their details
        if not created:
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        # Create or update the UserProfile with the phone number
        user_profile, profile_created = UserProfile.objects.get_or_create(user=user)
        user_profile.phone_number = phone_number
        user_profile.save()

        # Check for an existing OTP
        user_otp, created = UserOTP.objects.update_or_create(
            user=user,
            defaults={'otp': str(random.randint(1000, 9999))}
        )

        # If OTP exists but is expired, update it
        if not created and user_otp.is_expired():
            user_otp.otp = str(random.randint(1000, 9999))  # Generate a new OTP
            user_otp.created_at = timezone.now()  # Reset creation time
            user_otp.save()

        subject = 'Your OTP Code'
        message = self.get_email_html(user_otp.otp)

        try:
            # Send the OTP email
            send_mail(
                subject,
                message,
                os.getenv('EMAIL_HOST_USER'),
                [recipient],
                fail_silently=False,
                html_message=message  # Include the HTML message here
            )
            return Response({"status": "OTP sent successfully!"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_email_html(self, otp):
        return format_html(
            """
            <html>
                <body>
                    <h2 style="color: #4CAF50;">Your OTP Code</h2>
                    <p style="font-size: 16px;">Dear User,</p>
                    <p style="font-size: 16px;">Your One-Time Password (OTP) is:</p>
                    <h3 style="color: #2196F3;">{}</h3>
                    <p style="font-size: 16px;">Please enter this code to verify your email address.</p>
                    <p style="font-size: 16px;">Thank you!</p>
                    <footer style="font-size: 12px; color: #777;">
                        <p>This is an automated message. Please do not reply.</p>
                    </footer>
                </body>
            </html>
            """,
            otp
        )
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class VerifyOTPView(generics.CreateAPIView):
    serializer_class = VerifyOTPSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        try:
            user_otp = UserOTP.objects.get(user__email=email)

            # Check if OTP has expired
            if user_otp.is_expired():
                return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the OTP is correct
            if user_otp.otp == otp:
                return Response({"status": "OTP verified successfully!"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        except UserOTP.DoesNotExist:
            return Response({"error": "OTP not found."}, status=status.HTTP_404_NOT_FOUND)
        
        
        
        
from rest_framework.views import APIView
class PartyCreateView(APIView):
    def post(self, request, *args, **kwargs):
        # Get the email from the request data
        email = request.data.get('email')
        
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Find the user associated with the email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        # Remove 'user' field from party data before passing to serializer
        party_data = {key: value for key, value in request.data.items() if key != 'user'}

        # Pass the updated data to the serializer
        serializer = PartySerializer(data=party_data)

        if serializer.is_valid():
            # Manually assign the 'user' field when saving
            party = serializer.save(user=user)  # Use the user instance here
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Log the errors for better insight
        print(serializer.errors)  # Debugging: This will print the specific errors in the terminal.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class PartyByEmailView(APIView):
    def get(self, request, *args, **kwargs):
        # Get the email from the URL parameters
        email = request.query_params.get('email')
        
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Find the user associated with the email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Find all the parties associated with this user
        parties = Party.objects.filter(user=user)

        # Serialize the parties
        serializer = PartySerializer(parties, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)