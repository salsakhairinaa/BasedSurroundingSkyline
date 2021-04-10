from django.contrib import admin
from django.urls import path
from . import views

app_name = 'basedsurrounding'

urlpatterns = [
    #path('', views.first_form),
    path('', views.dashboard, name='dashboard'),
]
