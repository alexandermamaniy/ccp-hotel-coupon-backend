from django.contrib import admin
from coupons.models import Coupon
from user_profiles.admin import CouponUserProfileInline

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    inlines = (CouponUserProfileInline,)