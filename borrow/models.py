from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    USER_TYPES = (
        ('admin', '档案室管理员'),
        ('internal', '内部借阅人员'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='internal')
    department = models.CharField(max_length=100, blank=True, null=True)
    contact_info = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"
    
    class Meta:
        permissions = [
            ("can_manage_archives", "可以管理档案"),
            ("can_borrow_archives", "可以借阅档案"),
        ]