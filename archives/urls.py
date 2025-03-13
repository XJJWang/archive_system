from django.urls import path
from . import views

app_name = 'archives'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.archives_login, name='login'),
    path('logout/', views.archives_logout, name='logout'),
    path('create-archive-box/', views.create_archive_box, name='create_archive_box'),
    path('archive-box/<int:pk>/', views.archive_box_detail, name='archive_box_detail'),
    path('add-archives/', views.add_archives, name='add_archives'),
    path('ajax/load-cabinets/', views.load_cabinets, name='ajax_load_cabinets'),
    path('ajax/load-slots/', views.load_slots, name='ajax_load_slots'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('projects/create/', views.create_project, name='create_project'),
    path('projects/<int:pk>/edit/', views.edit_project, name='edit_project'),
    path('initialize-cabinets/', views.initialize_cabinets, name='initialize_cabinets'),
]