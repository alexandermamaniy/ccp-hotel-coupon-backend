from itertools import count

from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from coupons.models import Coupon
from coupons.serializers import CouponSerializer, CouponCreateSerializer
from hotelier_profiles.models import HotelierProfile
from user_profiles.models import UserProfile

class ListCouponsMeAPIView(ListAPIView):
    # serializer_class = BuddyProfileSerializer

    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_authenticated = UserProfile.objects.get(user=self.request.user)
        coupons = Coupon.objects.filter(profiles=user_authenticated)
        return coupons

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data)


class ListCouponsHotelierAPIView(ListAPIView):
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        hotelier_authenticated = HotelierProfile.objects.get(user=self.request.user)
        coupons = Coupon.objects.filter(hotelier_profile=hotelier_authenticated)
        return coupons

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data)

class ListAllCouponsAPIView(ListAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]



class CreateCouponUserAuthenticated(CreateAPIView):
    serializer_class = CouponCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['hotelier'] = self.request.user
        return context

    # def perform_create(self, serializer):
    #     h = HotelierProfile.objects.get(user=self.request.user)
    #     serializer.save(hotelier_profile=h )

    @extend_schema(
        request=CouponCreateSerializer,
        responses={201: CouponSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)



class RedeemCouponRetrieveAPIView(RetrieveAPIView):
    serializer_class = CouponSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        coupon_id = self.kwargs.get('pk')
        user_authenticated = UserProfile.objects.get(user=self.request.user)
        coupon = Coupon.objects.get(id=coupon_id)

        if coupon.profiles.filter(user=self.request.user).exists():
            raise Exception("You have already redeemed this coupon")

        user_authenticated.coupons.add(coupon)
        user_authenticated.save()
        return coupon

    def retrieve(self, request, *args, **kwargs):
        try:
            # Get the model instance
            queryset = self.get_object()

            # Instantiate the serializer
            serializer = self.get_serializer(queryset, context={'request': request})

            # Return the serialized data
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e), status=400)