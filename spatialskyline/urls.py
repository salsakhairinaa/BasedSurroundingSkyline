from django.urls import path
from . import views

app_name = 'spatialskyline'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('kueri/', views.kueri, name='kueri'),
    path('result/', views.result, name='result'),
]
