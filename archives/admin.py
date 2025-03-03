from django.contrib import admin
from .models import ArchiveRoom, Cabinet, Slot, ArchiveBox, Archive

@admin.register(ArchiveRoom)
class ArchiveRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'cabinet_count')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    
    def cabinet_count(self, obj):
        return obj.cabinets.count()
    cabinet_count.short_description = '柜子数量'

@admin.register(Cabinet)
class CabinetAdmin(admin.ModelAdmin):
    list_display = ('cabinet_number', 'archive_room', 'rows', 'columns', 'slot_count')
    list_filter = ('archive_room',)
    search_fields = ('cabinet_number', 'archive_room__name')
    
    def slot_count(self, obj):
        return obj.slots.count()
    slot_count.short_description = '格子数量'

@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ('cabinet', 'side', 'row', 'column', 'is_occupied', 'get_box_name')
    list_filter = ('cabinet__archive_room', 'cabinet', 'side', 'is_occupied')
    search_fields = ('cabinet__cabinet_number',)
    
    def get_box_name(self, obj):
        try:
            return obj.archive_box.name if hasattr(obj, 'archive_box') else '空'
        except:
            return '空'
    get_box_name.short_description = '档案盒名称'

# 先取消注册任何可能的ArchiveBox管理类，以避免冲突
try:
    admin.site.unregister(ArchiveBox)
except:
    pass

# 重新注册ArchiveBox
@admin.register(ArchiveBox)
class ArchiveBoxAdmin(admin.ModelAdmin):
    list_display = ('name', 'document_number', 'date', 'description', 'get_location', 'is_special', 'created_at', 'archive_count')
    list_filter = ('is_special', 'date', 'created_at', 'slot__cabinet__archive_room')
    search_fields = ('name', 'document_number', 'description')
    
    def get_location(self, obj):
        return obj.get_location_description()
    get_location.short_description = '位置'
    
    def archive_count(self, obj):
        if obj.is_special:
            return '特殊项目'
        return obj.archives.count()
    archive_count.short_description = '档案数量'

@admin.register(Archive)
class ArchiveAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'box', 'get_location', 'import_date', 'copy_count', 'is_in_stock')
    list_filter = ('import_date', 'is_in_stock', 'box__is_special')
    search_fields = ('title', 'description', 'box__name')
    raw_id_fields = ('box',)
    
    def get_location(self, obj):
        return obj.box.get_location_description() if obj.box else '未知'
    get_location.short_description = '位置'
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # 限制只能选择非特殊档案盒
        form.base_fields['box'].queryset = ArchiveBox.objects.filter(is_special=False)
        return form