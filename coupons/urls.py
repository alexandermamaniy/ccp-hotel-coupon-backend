from django.urls import path
from coupons.views import ListCouponsMeAPIView, ListAllCouponsAPIView, ListCouponsHotelierAPIView, \
    CreateCouponUserAuthenticated, RedeemCouponRetrieveAPIView

urlpatterns = [
    path('coupon/me', ListCouponsMeAPIView.as_view(), name='coupon-me'),
    path('coupon/', ListAllCouponsAPIView.as_view(), name='list-user-coupon'),
    path('coupon/hotelier', ListCouponsHotelierAPIView.as_view(), name='list-hotelier-coupon'),
    path('coupon/create-hotelier', CreateCouponUserAuthenticated.as_view(), name='create-hotelier-coupon'),
    path('coupon/redeem/<uuid:pk>', RedeemCouponRetrieveAPIView.as_view(), name='redeem-coupon'),
]

