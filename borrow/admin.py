from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile

# 将UserProfile作为User的内联显示
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = '用户资料'
    verbose_name_plural = '用户资料'

# 扩展User管理界面
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_user_type')
    list_filter = BaseUserAdmin.list_filter + ('groups',)
    
    def get_user_type(self, obj):
        try:
            return obj.profile.get_user_type_display()
        except UserProfile.DoesNotExist:
            return '未设置'
    
    get_user_type.short_description = '用户类型'

# 重新注册User模型
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# 单独注册UserProfile以便直接管理
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'department', 'contact_info']
    list_filter = ['user_type']
    search_fields = ['user__username', 'department', 'contact_info']
