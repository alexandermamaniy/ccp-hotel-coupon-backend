from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from hotelier_profiles.models import HotelierProfile
from hotelier_profiles.serializers import HotelierProfileSerializer
from user_profiles.models import UserProfile
from user_profiles.serializers import UserProfileSerializer
from .serializers import UserSerializer

# Create your views here.

class RetrieveGetProfileAPIView(RetrieveAPIView):
    # serializer_class = BuddyProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            hotelier = HotelierProfile.objects.get(user=self.request.user)
            obj = hotelier
        except HotelierProfile.DoesNotExist:
            try:
                obj = UserProfile.objects.get(user=self.request.user)
            except UserProfile.DoesNotExist:
                raise ObjectDoesNotExist("No profile found for the user.")

        self.check_object_permissions(self.request, obj)
        return obj



    def retrieve(self, request, *args, **kwargs):
        # Get the model instance
        queryset = self.get_object()

        if isinstance(queryset, HotelierProfile):
            serializer = HotelierProfileSerializer(queryset, context={'request': request})
        else:
            serializer = UserProfileSerializer(queryset, context={'request': request})
        # Instantiate the serializer
        # serializer = self.get_serializer(queryset, context={'request': request})

        # Return the serialized data
        return Response(serializer.data)
