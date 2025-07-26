from django.urls import path
from .import views

app_name = 'Pcos'

urlpatterns=[
	path('pcos/auth', views.pcos, name='pcos'),	
	path('pcos/patients_list', views.patients_list, name='patients_list'),
	path('pcos/view_full/<str:pk>', views.view_full, name='view_full'),
	path('pcos/add_patient', views.add_patient, name='add_patient'),
	path('pcos/edit_patient/<str:pk>', views.edit_patient, name='edit_patient'),
	path('pcos/add_visit/<str:pk>', views.add_visit, name='add_visit'),
	path('pcos/edit_visit/<str:vk>', views.edit_visit, name='edit_visit'),
	path('pcos/add_appointment/<str:pk>/<str:vk>', views.add_appointment, name='add_appointment'),
	path('pcos/edit_appointment/<str:ak>', views.edit_appointment, name='edit_appointment'),
	path('pcos/add_ultrasound/<str:pk>/<str:vk>', views.add_ultrasound, name='add_ultrasound'),
	path('pcos/edit_ultrasound/<str:uk>', views.edit_ultrasound, name='edit_ultrasound'),
	path('pcos/add_laboratory/<str:pk>/<str:vk>', views.add_laboratory, name='add_laboratory'),
	path('pcos/edit_laboratory/<str:lk>', views.edit_laboratory, name='edit_laboratory'),
	path('pcos/calculate_age', views.calculate_age, name='calculate_age'),
	path('pcos/get_ethnicity', views.get_ethnicity, name='get_ethnicity'),
	path('pcos/execute_query', views.execute_query, name='execute_query'),
	path('pcos/logout_user', views.logout_user, name='logout_user'),
    path('pcos/docs', views.export_to_document, name='docs'),
    path('pcos/report_filework', views.report_filework, name='report_filework'),
    path('pcos/report_exportdata', views.report_exportdata, name='report_exportdata'),
]
	




	
