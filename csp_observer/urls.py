from django.urls import path
from . import views

urlpatterns = [
    path('report/<str:report_type>/<uuid:session_id>', views.report, name='report'),
    path('result/<uuid:session_id>', views.result, name='result'),
    path('master/session/<uuid:session_id>', views.master_session, name='master_session'),
    path('admin/', views.csprequest_list, name='admin'),
]