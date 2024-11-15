from django.urls import path
from .views import *

urlpatterns = [
    path('user-posts', UserPostCreate.as_view(), name='user-post-create'),
    path('user-data/', GetUserDataView.as_view(), name='get-user-data'),
    path('send-email', SendEmailView.as_view(), name='send-email'),
    path('verify-otp', VerifyOTPView.as_view(), name='verify-otp'),
]
