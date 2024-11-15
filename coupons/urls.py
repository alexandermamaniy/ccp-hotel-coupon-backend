from django.urls import path
from coupons.views import ListCouponsMeAPIView, ListAllCouponsAPIView, ListCouponsHotelierAPIView, \
    CreateCouponUserAuthenticated, RedeemCouponRetrieveAPIView, UseCouponRetrieveAPIView, ListCouponsUsedAPIView

urlpatterns = [
    path('coupon/me', ListCouponsMeAPIView.as_view(), name='coupon-me'),
    path('coupon/', ListAllCouponsAPIView.as_view(), name='list-user-coupon'),
    path('coupon/hotelier', ListCouponsHotelierAPIView.as_view(), name='list-hotelier-coupon'),
    path('coupon/create-hotelier', CreateCouponUserAuthenticated.as_view(), name='create-hotelier-coupon'),
    path('coupon/redeem/<uuid:pk>', RedeemCouponRetrieveAPIView.as_view(), name='redeem-coupon'),
    path('coupon/use/<uuid:pk>', UseCouponRetrieveAPIView.as_view(), name='coupon-used'),
    path('coupon/list-used', ListCouponsUsedAPIView.as_view(), name='list-coupon-used'),
]

