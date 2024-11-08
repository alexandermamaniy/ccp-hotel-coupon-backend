from rest_framework.serializers import ModelSerializer

from hotelier_profiles.models import HotelierProfile
from users.serializers import UserSerializer


class HotelierProfileSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = HotelierProfile
        fields = ['id', 'user', 'name', 'telephone', 'country', 'address', 'picture_url', 'is_active']
