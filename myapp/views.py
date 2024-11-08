from rest_framework import generics, status, serializers
from rest_framework.response import Response
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .models import UserPost, UserOTP
from .serializers import UserPostSerializer, EmailSerializer
import os
import random
from django.utils.html import format_html

class UserPostCreate(generics.CreateAPIView):
    queryset = UserPost.objects.all()
    serializer_class = UserPostSerializer

class SendEmailView(generics.CreateAPIView):
    serializer_class = EmailSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        recipient = serializer.validated_data['recipient']
        
        # Attempt to get the user by email; create if not exists
        user, created = User.objects.get_or_create(email=recipient, defaults={'username': recipient})

        # Generate a random 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Store OTP in the database
        UserOTP.objects.update_or_create(user=user, defaults={'otp': otp})

        subject = 'Your OTP Code'
        message = self.get_email_html(otp)

        try:
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

            if user_otp.is_expired():
                return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

            if user_otp.otp == otp:
                return Response({"status": "OTP verified successfully!"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)
        except UserOTP.DoesNotExist:
            return Response({"error": "OTP not found."}, status=status.HTTP_404_NOT_FOUND)
