from django.urls import path
from . import views
from .update import update_rules

urlpatterns = [
    path('report/<str:report_type>/<uuid:session_id>', views.report, name='report'),
    path('result/<uuid:session_id>', views.result, name='result'),
    path('resultdetail/<uuid:session_id>', views.result_detail, name='result_detail'),
    path('master/session/<uuid:session_id>', views.master_session, name='master_session'),
    path('privacy/', views.privacy, name='privacy'),
    path('admin/', views.admin, name='admin'),
]
