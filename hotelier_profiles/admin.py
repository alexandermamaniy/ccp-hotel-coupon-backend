from django.contrib import admin
from hotelier_profiles.models import HotelierProfile

admin.site.register(HotelierProfile)


# @admin.register(HotelierProfile)
# class BuddyExpenseAdmin(admin.ModelAdmin):
#     # filter_horizontal = ("group_members",)
#     filter_horizontal = ('coupons',)

#
#
# from django.contrib import admin
# from .models import TodoList
#
#
#
# class HotelierAdmin(admin.ModelAdmin):
# 	filter_horizontal = ('todolist',)
#
# admin.site.register(TodoList)