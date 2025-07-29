from django.urls import path
from . import views

app_name = 'fdb'

urlpatterns = [
    path('fdb/storage/', views.storage_service_view, name='storage'),
    path('fdb/data/', views.data_service_view, name='data'),
    path('fdb/visualization/', views.visualization_service_view, name='visualization'),
    path('fdb/missing/', views.missing_data_service_view, name='missing_data'),
    path('fdb/statistics/', views.statistics_service_view, name='statistics'),

    path('fdb/auth/', views.auth_service_view, name='auth'),
    path('fdb/register/', views.register_view, name='register'),
    path('fdb/reset-password/', views.reset_password_view, name='reset_password'),
    path('fdb/logout/', views.logout_view, name='logout'),
]