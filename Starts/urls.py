from django.urls import path
from .import views


app_name = 'Starts'

urlpatterns=[
	path('', views.index, name='index'),
	path('analysis', views.analysis, name='analysis'),
	path('products', views.products, name='products'),
	path('contacts', views.contacts, name='contacts'),
	]