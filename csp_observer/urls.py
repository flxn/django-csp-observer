from django.urls import path
from . import views
from .update import update_rules

urlpatterns = [
    # business logic
    path('report/<str:report_type>/<uuid:session_id>', views.report, name='report'),
    path('result/<uuid:session_id>', views.result, name='result'),
    path('resultdetail/<uuid:session_id>', views.result_detail, name='result_detail'),
    path('master/session/<uuid:session_id>', views.master_session, name='master_session'),
    path('session/<uuid:session_id>/share', views.share_session, name='share_session'),

    # admin
    path('admin/', views.admin, name='admin'),
    path('admin/update/rules/', views.admin_update_rules, name='admin_update_rules'),
    path('admin/rule/<int:rule_id>/delete', views.delete_custom_rule, name='delete_custom_rule'),
    path('chart/observed_rule_distribution', views.chart_observed_rule_distribution, name='chart_observed_rule_distribution'),
    path('chart/reports_per_day', views.chart_reports_per_day, name='chart_reports_per_day'),

    # other
    path('privacy/', views.privacy, name='privacy'),
]
