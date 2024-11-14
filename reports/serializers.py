from rest_framework.serializers import ModelSerializer
from hotelier_profiles.serializers import HotelierProfileSerializer
from reports.models import Report


class ReportSerializer(ModelSerializer):
    hotelier_profile = HotelierProfileSerializer

    class Meta:
        model = Report
        fields = ['id', 'title', 'media_url', 'hotelier_profile', 'created_date']
