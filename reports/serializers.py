from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from hotelier_profiles.serializers import HotelierProfileSerializer
from reports.models import Report


class ReportSerializer(ModelSerializer):
    hotelier_profile = HotelierProfileSerializer

    class Meta:
        model = Report
        fields = ['id', 'title', 'media_url', 'hotelier_profile', 'created_date']


class ReportTableHeaderSerializer(serializers.Serializer):
    column1 = serializers.CharField()
    column2 = serializers.CharField()
    column3 = serializers.CharField()
    column4 = serializers.CharField()

class ReportTableBodySerializer(serializers.Serializer):
    column1 = serializers.CharField()
    column2 = serializers.CharField()
    column3 = serializers.CharField()
    column4 = serializers.CharField()

class CustomReportSerializer(serializers.Serializer):
    report_title = serializers.CharField()
    report_description = serializers.CharField()
    report_table_data_header = ReportTableHeaderSerializer()
    report_table_data_body = ReportTableBodySerializer(many=True)