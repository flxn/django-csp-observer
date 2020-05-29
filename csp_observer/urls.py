from django.urls import path

from . import views

urlpatterns = [
    path('report/<uuid:session_id>/', views.report, name='report')
]