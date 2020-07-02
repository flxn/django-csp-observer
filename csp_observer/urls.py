from django.urls import path

from . import views

urlpatterns = [
    path('report/<str:report_type>/<uuid:session_id>/', views.report, name='report'),
    path('result/<uuid:session_id>/', views.result, name='result'),
    path('admin/', views.admin, name='admin'),
]