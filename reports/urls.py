from django.urls import path
from .views import GenerateReportPDFView, ListReportAPIView

urlpatterns = [
    path('report/generate-pdf', GenerateReportPDFView.as_view(), name='generate-report-pdf'),
    path('report/me', ListReportAPIView.as_view(), name='report-pdf-me'),

]