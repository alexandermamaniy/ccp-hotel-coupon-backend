from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from coupons.models import Coupon
from .aws_resources import SQSPoller
from .models import Report
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.base import ContentFile
import datetime

from .report_generator import generate_pdf
from hotelier_profiles.models import HotelierProfile
from functools import partial

import boto3
import json

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


def my_message_handler(message, buffer_data, hotelier_coupon_ids, from_date_report):
    # Process the message
    print("Processing message:", message['Body'])
    message = json.loads(message['Body'])
    # Return True if processed successfully, False otherwise

    print(str(message['date']))
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
        # Generate PDF content



        hotelier_authenticated = HotelierProfile.objects.get(user=self.request.user)
        hotelier_coupons = Coupon.objects.filter(hotelier_profile=hotelier_authenticated)

        hotelier_coupon_ids = [str(coupon.id) for coupon in hotelier_coupons]

        buffer_data = []
        queue_poller = SQSPoller()

        from_date_report = datetime.datetime.now().date()


        handler_with_params = partial(my_message_handler, buffer_data=buffer_data, hotelier_coupon_ids=hotelier_coupon_ids, from_date_report=from_date_report)
        queue_poller.poll_messages(handler_with_params, target_message_count=30)

        processed_data = {}
        current_day = datetime.datetime.now().date()

        coupon_gral_information = {}

        for coupon in hotelier_coupons:
            coupon_gral_information[str(coupon.id)] = {}
            coupon_gral_information[str(coupon.id)]['title'] = str(coupon.title)
            coupon_gral_information[str(coupon.id)]['how_many_have_redeemed'] = str(coupon.how_many_have_redeemed)
            coupon_gral_information[str(coupon.id)]['how_many_have_used'] = str(coupon.how_many_have_used)
            coupon_gral_information[str(coupon.id)]['quantity'] = str(coupon.quantity)
            coupon_gral_information[str(coupon.id)]['discount'] = str(coupon.discount)


        for data in buffer_data:
            if not data['coupon_id'] in processed_data:
                processed_data[data['coupon_id']] = {}
                processed_data[data['coupon_id']]['view'] = 0
                processed_data[data['coupon_id']]['redeem'] = 0
                coupon_target = Coupon.objects.get(id=str(data['coupon_id']))
                processed_data[data['coupon_id']]['coupon_title'] =  str(coupon_target.title)

            processed_data[data['coupon_id']][data['action']] += 1
        hotelier_name = str(hotelier_authenticated.name)
        pdf_buffer = generate_pdf(processed_data, coupon_gral_information, from_date_report, current_day, hotelier_name)


        # Save the PDF to the report_url field, which will upload it to S3
        pdf_filename = f"{datetime.datetime.now().isoformat()}.pdf"

        # Create a new ReportTime instance

        report_name = current_day.isoformat() + "-" + hotelier_name + "-Report"

        report_instance = Report(hotelier_profile=hotelier_authenticated, title=report_name)

        report_instance.media_url.save(pdf_filename, ContentFile(pdf_buffer.read()), save=True)

        # PUSH to SNS
        message = {"hotelier_id": str(hotelier_authenticated.id)}
        client = boto3.client('sns', region_name='us-east-1')
        response = client.publish(
            TargetArn="arn:aws:sns:us-east-1:851725189998:ReportNotification",
            Message=json.dumps(message),
        )

        print(response)

        return Response({'pdf_url': report_instance.media_url.url}, status=status.HTTP_201_CREATED)
