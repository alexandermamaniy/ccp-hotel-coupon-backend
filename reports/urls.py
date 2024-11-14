from django.urls import path
from .views import GenerateReportPDFView

urlpatterns = [
    path('generate-report-pdf/', GenerateReportPDFView.as_view(), name='generate-report-pdf'),
]