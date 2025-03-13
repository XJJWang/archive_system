from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('archives/', include('archives.urls')),  # 现有的档案管理系统
    path('borrow/', include('borrow.urls')),      # 新的借阅系统
    
    # 将网站根路径重定向到借阅系统首页
    path('', RedirectView.as_view(url='/borrow/', permanent=False)),
]

# 添加媒体文件的URL配置
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)