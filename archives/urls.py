from django.urls import path
from . import views
from .views import PlaceArchiveBoxView

urlpatterns = [
    path('', views.home, name='home'),
    path('cabinets/<int:cabinet_id>/', views.cabinet_slots, name='cabinet_slots'),
    path('api/available-slots/', views.get_available_slots, name='get_available_slots'),
    path('archives/create/', views.ArchiveCreateView.as_view(), name='archive_create'),
    path('archives/', views.ArchiveListView.as_view(), name='archive_list'),
    path('archives/<int:pk>/', views.ArchiveDetailView.as_view(), name='archive_detail'),
    path('place-archive-box/', PlaceArchiveBoxView.as_view(), name='place_archive_box'),

]