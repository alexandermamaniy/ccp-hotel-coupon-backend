from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from coupons.models import Coupon
from .models import Report
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile
import datetime

from hotel_coupon_app_package_alexandermamani.report_pdf import ReportPDF
from hotel_coupon_app_package_alexandermamani.aws_services import SQSService, SNSService, SNSPublishMessageError, SQSPollingMessagesError, SQSClosingConnectionError



from hotelier_profiles.models import HotelierProfile
from functools import partial
import json

import environ


from .serializers import ReportSerializer


class ListReportAPIView(ListAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        hotelier_authenticated = HotelierProfile.objects.get(user=self.request.user)
        reports = Report.objects.filter(hotelier_profile=hotelier_authenticated)
        return reports

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data)


def handler_to_get_data_for_a_specific_hotelier_id(message, buffer_data, hotelier_coupon_ids, from_date_report):
    """
    Return True if the user interaction data is part of their own hotelier coupons, False otherwise.

    When True: Add the interaction user message to the buffer_data list and delete it from AWS SQS Queue.
    When False: keep the interaction user message to AWS SQS Queue.
    """
    message = json.loads(message['Body'])
    # Return True if processed successfully, False otherwise

    date_object = datetime.datetime.strptime(str(message['date']), '%d-%m-%Y').date()

    if from_date_report < date_object:
        from_date_report = date_object

    if message['coupon_id'] in hotelier_coupon_ids:
        buffer_data.append(message)
        return True
    else:
        return False

class GenerateReportPDFView(APIView):
    def get(self, request, *args, **kwargs):

        env = environ.Env()

        hotelier_authenticated = HotelierProfile.objects.get(user=self.request.user)
        hotelier_coupons = Coupon.objects.filter(hotelier_profile=hotelier_authenticated)

        hotelier_coupon_ids = [str(coupon.id) for coupon in hotelier_coupons]

        buffer_processed_data = []

        AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
        AWS_REGION = env('AWS_REGION')
        AWS_SQS_QUEUE_URL = env('AWS_SQS_QUEUE_URL')

        sqs_queue_instance = SQSService(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                  aws_region=AWS_REGION,
                                  aws_sqs_queue_url=AWS_SQS_QUEUE_URL)

        from_date_report = datetime.datetime.now().date()

        handler_with_buffer = partial(handler_to_get_data_for_a_specific_hotelier_id, buffer_data=buffer_processed_data, hotelier_coupon_ids=hotelier_coupon_ids, from_date_report=from_date_report)

        try:
            sqs_queue_instance.poll_messages(handler_with_buffer, target_message_count=30)
            sqs_queue_instance.close()
        except (SQSPollingMessagesError, SQSClosingConnectionError) as e:
            print("Error SQS", e)

        user_interaction_data = {}
        current_day = datetime.datetime.now().date()

        coupon_gral_information = {}

        for coupon in hotelier_coupons:
            coupon_gral_information[str(coupon.id)] = {}
            coupon_gral_information[str(coupon.id)]['title'] = str(coupon.title)
            coupon_gral_information[str(coupon.id)]['how_many_have_redeemed'] = str(coupon.how_many_have_redeemed)
            coupon_gral_information[str(coupon.id)]['how_many_have_used'] = str(coupon.how_many_have_used)
            coupon_gral_information[str(coupon.id)]['quantity'] = str(coupon.quantity)
            coupon_gral_information[str(coupon.id)]['discount'] = str(coupon.discount)


        for data in buffer_processed_data:
            if not data['coupon_id'] in user_interaction_data:
                user_interaction_data[data['coupon_id']] = {}
                user_interaction_data[data['coupon_id']]['view'] = 0
                user_interaction_data[data['coupon_id']]['redeem'] = 0
                coupon_target = Coupon.objects.get(id=str(data['coupon_id']))
                user_interaction_data[data['coupon_id']]['coupon_title'] =  str(coupon_target.title)

            user_interaction_data[data['coupon_id']][data['action']] += 1

        hotelier_name = str(hotelier_authenticated.name)
        report = ReportPDF(user_interaction_data, coupon_gral_information, datetime.datetime.now().date(), hotelier_name)
        pdf_buffer = report.generate()

        # Save the PDF to the report_url field, which will upload it to S3
        pdf_filename = f"{datetime.datetime.now().isoformat()}.pdf"

        # Create a new ReportTime instance
        report_name = current_day.isoformat() + "-" + hotelier_name + "-Report"
        report_instance = Report(hotelier_profile=hotelier_authenticated, title=report_name)
        report_instance.media_url.save(pdf_filename, ContentFile(pdf_buffer.read()), save=True)

        # PUSH to SNS
        message = {"hotelier_id": str(hotelier_authenticated.id)}

        AWS_SNS_REPORT_NOTIFICATION_ARN = env('AWS_SNS_REPORT_NOTIFICATION_ARN')

        sns_service = SNSService(aws_access_key=AWS_ACCESS_KEY_ID, aws_secret_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_REGION)
        try:
             sns_service.publish_message(AWS_SNS_REPORT_NOTIFICATION_ARN, message, "Report Notification")
        except SNSPublishMessageError as e:
            print("SNS Error", e)

        return Response({'pdf_url': report_instance.media_url.url}, status=status.HTTP_201_CREATED)
