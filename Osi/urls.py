from django.urls import path, re_path
from django.views.generic import RedirectView
from . import views

app_name='Osi'

urlpatterns = [
    #instruction url
    path('osi/instruction', views.instruction_view, name='instruction'),
    #fields urls
    path('osi/fields_mode', views.fields_mode_view, name='fields_mode'),
    path('osi/fields_redirect', views.fields_redirect_view, name='fields_redirect'),
    path('osi/fields_data', views.fields_data_view, name='fields_data'),
    path('osi/fields_selection_col', views.fields_selection_col_view, name='fields_selection_col'),
    path('osi/fields_selection_col_value', views.fields_selection_col_value_view, name='fields_selection_col_value'),
    path('osi/fields_division_cols', views.fields_division_cols_view, name='fields_division_cols'),
    path('osi/fields_patient_info', views.fields_patient_info_view, name='fields_patient_info'),
    path('osi/fields_patient_num_params', views.fields_patient_num_params_view, name='fields_patient_num_params'),
    path('osi/fields_patient_den_params', views.fields_patient_den_params_view, name='fields_patient_den_params'),
    path('osi/fields_age_interval_borders', views.fields_age_interval_borders_view, name='fields_age_interval_borders'),
    path('osi/fields_results', views.fields_results_view, name='fields_results'),
    path('osi/fields_export_pdf', views.fields_export_pdf, name='export_pdf'),
    path('osi/fields_divide_by_ethnicity_default', views.fields_divide_by_ethnicity_default_view, name='divide_by_ethnicity_default'),
    path('osi/fields_patient_default', views.fields_patient_default_view, name='patient_default'),
    path('osi/fields_error', views.fields_error_view, name='fields_error'),
    #file urls
    path('osi/file_data', views.file_data_view, name='file_data'),
    path('osi/file_id_col', views.file_id_col_view, name='file_id_col'),
    path('osi/file_numerator_params_cols', views.file_numerator_params_cols_view,
         name='file_numerator_params_cols'),
    path('osi/file_denominator_params_cols', views.file_denominator_params_cols_view,
         name='file_denominator_params_cols'),
    path('osi/file_division_cols', views.file_division_cols_view, name='file_division_cols'),
    path('osi/file_gender_values_quantity', views.file_gender_values_quantity_view, name='file_gender_values_quantity'),
    path('osi/file_gender_values', views.file_gender_values_view, name='file_gender_values'),
    path('osi/file_ethnicity_values_quantity', views.file_ethnicity_values_quantity_view, name='file_ethnicity_values_quantity'),
    path('osi/file_ethnicity_values', views.file_ethnicity_values_view, name='file_ethnicity_values'),
    path('osi/file_age_intervals_quantity', views.file_age_intervals_quantity_view, name='file_age_intervals_quantity'),
    path('osi/file_age_intervals_borders', views.file_age_intervals_borders_view, name='file_age_intervals_borders'),
    path('osi/file_selection_col', views.file_selection_col_view, name='file_selection_col'),
    path('osi/file_selection_col_values', views.file_selection_col_values_view, name='file_selection_col_values'),
    path('osi/file_results', views.file_results_view, name='file_results'),
    path('osi/file_error', views.file_error_view, name='file_error'),

]
