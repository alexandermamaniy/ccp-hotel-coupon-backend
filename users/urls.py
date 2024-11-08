from django.urls import path

from users.views import RetrieveGetProfileAPIView

urlpatterns = [
    path('profile/me', RetrieveGetProfileAPIView.as_view(), name='profile-me'),
]