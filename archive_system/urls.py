from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('archives.urls')),  # 将 archives 应用的 URLs 包含到主项目中
]