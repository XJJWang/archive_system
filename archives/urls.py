from django.urls import path
from . import views

app_name = 'archives'

urlpatterns = [
    path('', views.home, name='home'),


]