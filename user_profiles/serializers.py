from rest_framework.serializers import ModelSerializer

from coupons.serializers import CouponSerializer
from user_profiles.models import UserProfile, CouponUserProfile
from users.serializers import UserSerializer


class UserProfileSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'full_name', 'coupons', 'picture_url','is_active']



class CouponUserProfileSerializer(ModelSerializer):
    user_profile_id = UserProfileSerializer()
    coupon_id = CouponSerializer()
    class Meta:
        model = CouponUserProfile
        fields = ['user_profile_id', 'coupon_id', 'is_used', 'id', 'created_date']
