from django import forms
from .models import Archive, Slot, Cabinet, ArchiveRoom, ArchiveBox

class ArchiveForm(forms.ModelForm):
    """档案录入表单"""
    
    # 新增档案盒字段
    box = forms.ModelChoiceField(
        queryset=ArchiveBox.objects.all(),
        label="档案盒",
        required=False  # 允许为空
    )
    
    # 用于选择位置的字段
    archive_room = forms.ModelChoiceField(
        queryset=ArchiveRoom.objects.all(),
        label="档案室",
        required=True
    )
    cabinet = forms.ModelChoiceField(
        queryset=Cabinet.objects.none(),
        label="柜子",
        required=True
    )
    side = forms.ChoiceField(
        choices=Slot.SIDE_CHOICES,
        label="侧面",
        required=True
    )
    row = forms.IntegerField(label="行号", min_value=1, required=True)
    column = forms.IntegerField(label="列号", min_value=1, required=True)
    
    class Meta:
        model = Archive
        fields = ['title', 'description', 'copy_count']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if 'archive_room' in self.data:
            try:
                archive_room_id = int(self.data.get('archive_room'))
                self.fields['cabinet'].queryset = Cabinet.objects.filter(archive_room_id=archive_room_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.slot:
            self.fields['cabinet'].queryset = Cabinet.objects.filter(archive_room=self.instance.slot.cabinet.archive_room)
            
    def clean(self):
        cleaned_data = super().clean()
        
        # 检查选择的位置是否存在且未被占用
        cabinet = cleaned_data.get('cabinet')
        side = cleaned_data.get('side')
        row = cleaned_data.get('row')
        column = cleaned_data.get('column')
        
        if cabinet and side and row is not None and column is not None:
            # 检查行列号是否在柜子范围内
            if row > cabinet.rows or column > cabinet.columns:
                raise forms.ValidationError("所选位置超出柜子的范围")
            
            # 检查所选位置是否已被占用
            try:
                slot = Slot.objects.get(
                    cabinet=cabinet,
                    side=side,
                    row=row,
                    column=column
                )
                if slot.is_occupied:
                    raise forms.ValidationError("所选位置已被占用")
            except Slot.DoesNotExist:
                # 如果格子不存在，会在视图中创建
                pass
                
        return cleaned_data


class ArchiveSearchForm(forms.Form):
    """档案搜索表单"""
    title = forms.CharField(label="标题", required=False)
    cabinet_number = forms.CharField(label="柜子编号", required=False)
    is_in_stock = forms.BooleanField(label="是否在库", required=False, initial=True)

class ArchiveBoxForm(forms.ModelForm):
    """档案盒表单"""
    
    class Meta:
        model = ArchiveBox
        fields = ['name', 'document_number', 'date', 'description', 'slot', 'is_special']
        # 不要包含box_number