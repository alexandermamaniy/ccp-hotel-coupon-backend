from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from coupons.models import Coupon
from coupons.serializers import CouponSerializer, CouponCreateSerializer
from hotel_coupon_app_package_alexandermamani.aws_services import SNSService, SNSPublishMessageError
from hotelier_profiles.models import HotelierProfile
from user_profiles.models import UserProfile, CouponUserProfile
from user_profiles.serializers import CouponUserProfileSerializer
from rest_framework import status
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import environ


class ListCouponsMeAPIView(ListAPIView):
    # serializer_class = BuddyProfileSerializer

    serializer_class = CouponUserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_authenticated = UserProfile.objects.get(user=self.request.user)
        coupons = CouponUserProfile.objects.filter(user_profile_id=user_authenticated, is_used=False)
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
    permission_classes = [IsAuthenticated]
    serializer_class = CouponSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['hotelier_profile__name', 'hotelier_profile__country']
    search_fields = ['title', 'description', 'hotelier_profile__name', 'hotelier_profile__address', 'hotelier_profile__country']



class CreateCouponUserAuthenticated(CreateAPIView):
    serializer_class = CouponCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['hotelier'] = self.request.user
        return context

    def create(self, request, *args, **kwargs):
        env = environ.Env()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
        AWS_REGION = env('AWS_REGION')
        AWS_SNS_NEW_COUPON_NOTIFICATION_ARN = env('AWS_SNS_NEW_COUPON_NOTIFICATION_ARN')

        hotelier_authenticated = HotelierProfile.objects.get(user=self.request.user)
        coupon = serializer.validated_data

        message = { "coupon_name": coupon['title'] ,
                    "hotel_name": str(hotelier_authenticated.name),
                    "hotelier_id":  str(hotelier_authenticated.id)}

        sns_service = SNSService(aws_access_key=AWS_ACCESS_KEY_ID,
                                 aws_secret_key=AWS_SECRET_ACCESS_KEY,
                                 region_name=AWS_REGION)
        try:
            print(message)
            print(AWS_SNS_NEW_COUPON_NOTIFICATION_ARN)
            print(sns_service.publish_message(AWS_SNS_NEW_COUPON_NOTIFICATION_ARN, message,
                                        "New Coupon released Notification"))
        except SNSPublishMessageError as e:
            print("SNS Error", e)

        # Return the serialized data
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=CouponCreateSerializer,
        responses={201: CouponSerializer}
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)



class RedeemCouponRetrieveAPIView(RetrieveAPIView):
    serializer_class = CouponUserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        coupon_id = self.kwargs.get('pk')
        user_authenticated = UserProfile.objects.get(user=self.request.user)
        coupon = Coupon.objects.get(id=coupon_id)

        if coupon.profiles.filter(user=self.request.user).exists():
            raise Exception("You have already redeemed this coupon")

        user_authenticated.coupons.add(coupon)
        coupon.how_many_have_redeemed += 1
        coupon.save()
        user_authenticated.save()
        coupon_with_code = CouponUserProfile.objects.get(user_profile_id=user_authenticated, coupon_id=coupon)
        return coupon_with_code

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

class UseCouponRetrieveAPIView(RetrieveAPIView):
    serializer_class = CouponUserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        coupon_code_id = self.kwargs.get('pk')

        coupon_with_code = CouponUserProfile.objects.get(id=coupon_code_id)
        coupon = coupon_with_code.coupon_id

        if coupon_with_code.is_used:
            raise Exception("You have already used this coupon")

        coupon_with_code.is_used = True
        coupon_with_code.save()
        coupon.how_many_have_used += 1
        coupon.save()
        return coupon_with_code

    def retrieve(self, request, *args, **kwargs):
        try:
            queryset = self.get_object()
            serializer = self.get_serializer(queryset, context={'request': request})
            user_profile_id = str(queryset.user_profile_id.id)
            coupon_code = str(queryset.id)
            message = {
                "user_profile_id": str(user_profile_id),
                "coupon_code": coupon_code}

            env = environ.Env()

            AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
            AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
            AWS_REGION = env('AWS_REGION')
            AWS_SNS_USED_COUPON_NOTIFICATION_ARN = env('AWS_SNS_USED_COUPON_NOTIFICATION_ARN')

            sns_service = SNSService(aws_access_key=AWS_ACCESS_KEY_ID,
                                     aws_secret_key=AWS_SECRET_ACCESS_KEY,
                                     region_name=AWS_REGION)
            try:
                sns_service.publish_message(AWS_SNS_USED_COUPON_NOTIFICATION_ARN, message,
                                                               "Report Used Coupon Notification")
            except SNSPublishMessageError as e:
                print("SNS Error", e)
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e), status=400)

class ListCouponsUsedAPIView(ListAPIView):
    serializer_class = CouponUserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        hotelier_authenticated = HotelierProfile.objects.get(user=self.request.user)
        coupons = Coupon.objects.filter(hotelier_profile=hotelier_authenticated)
        list_coupon_used = []
        for coupon in coupons:
            coupons_used = CouponUserProfile.objects.filter(coupon_id=coupon, is_used=True)
            list_coupon_used.extend(coupons_used)
        return list_coupon_used

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data)
