from coupons.models import Coupon
from rest_framework import serializers

from hotelier_profiles.models import HotelierProfile
from hotelier_profiles.serializers import HotelierProfileSerializer

# Serializar to expose API to create a coupon and their fields
class CouponCreateSerializer(serializers.ModelSerializer):
    media_url = serializers.ImageField(required=False)

    class Meta:
        model = Coupon
        fields = ['title', 'description', 'discount', 'media_url', 'quantity', 'expiration_date']

    def create(self, validated_data):
        user = self.context.get('hotelier')
        hotelier_authenticated = HotelierProfile.objects.get(user=user)
        coupon = Coupon.objects.create(hotelier_profile=hotelier_authenticated, **validated_data)
        return coupon

# Serializar to expose API to list all coupons and their fields, more information about the hotelier
class CouponSerializer(serializers.ModelSerializer):
    hotelier_profile = HotelierProfileSerializer()
    class Meta:
        model = Coupon
        fields = ['id', 'title', 'description', 'discount', 'media_url', 'quantity', 'how_many_have_redeemed', 'expiration_date', 'hotelier_profile']
