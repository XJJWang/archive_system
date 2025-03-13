from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from borrow.models import UserProfile

class Command(BaseCommand):
    help = '创建用户组和分配权限'

    def handle(self, *args, **options):
        # 创建用户组
        admin_group, _ = Group.objects.get_or_create(name='档案室管理员')
        internal_group, _ = Group.objects.get_or_create(name='内部借阅人员')
        
        # 获取内容类型
        profile_content_type = ContentType.objects.get_for_model(UserProfile)
        
        # 获取或创建权限
        manage_archives_perm, _ = Permission.objects.get_or_create(
            codename='can_manage_archives',
            name='可以管理档案',
            content_type=profile_content_type,
        )
        
        borrow_archives_perm, _ = Permission.objects.get_or_create(
            codename='can_borrow_archives',
            name='可以借阅档案',
            content_type=profile_content_type,
        )
        
        # 分配权限给用户组
        admin_group.permissions.add(manage_archives_perm, borrow_archives_perm)
        internal_group.permissions.add(borrow_archives_perm)
        
        self.stdout.write(self.style.SUCCESS('成功创建用户组和权限'))