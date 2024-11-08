from rest_framework.serializers import ModelSerializer

from user_profiles.models import UserProfile
from users.serializers import UserSerializer


class UserProfileSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'full_name', 'coupons', 'picture_url', 'is_active']
