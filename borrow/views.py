from django.shortcuts import render

# Create your views here.

def home(request):
    """借阅系统首页"""
    return render(request, 'borrow/home.html')
