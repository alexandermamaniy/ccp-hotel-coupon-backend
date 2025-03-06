from django.urls import path
from .views import GenerateReportPDFView, ListReportAPIView, GenerateReportPDFCustomView

urlpatterns = [
    path('report/generate-pdf', GenerateReportPDFView.as_view(), name='generate-report-pdf'),
    path('report/me', ListReportAPIView.as_view(), name='report-pdf-me'),
    path('generate_pdf', GenerateReportPDFCustomView.as_view(), name='report-pdf'),
]