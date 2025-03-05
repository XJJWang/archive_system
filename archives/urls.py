from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('create-archive-box/', views.create_archive_box, name='create_archive_box'),
    path('add-archives/', views.add_archives, name='add_archives'),
    path('ajax/load-cabinets/', views.load_cabinets, name='ajax_load_cabinets'),
    path('ajax/load-slots/', views.load_slots, name='ajax_load_slots'),
]