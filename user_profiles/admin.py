
from django.contrib import admin
from user_profiles.models import UserProfile


class CouponUserProfileInline(admin.TabularInline):
    model = UserProfile.coupons.through

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # filter_horizontal = ("group_members")
    # filter_horizontal = ('coupons',)
    inlines = (CouponUserProfileInline,)
    exclude = ('coupons',)