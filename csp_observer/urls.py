from django.urls import path

from . import views

urlpatterns = [
    path('report/<uuid:report_id>/', views.report, name='report')
]