from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.views import View

from .models import ArchiveRoom, Cabinet, Slot, Archive, ArchiveBox
from .forms import ArchiveForm, ArchiveSearchForm

def home(request):
    """首页视图"""
    rooms = ArchiveRoom.objects.all().prefetch_related('cabinets', 'cabinets__slots')
    return render(request, 'archives/home.html', {
        'rooms': rooms
    })
