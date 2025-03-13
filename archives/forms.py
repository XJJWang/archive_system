from django import forms
from django.forms import widgets, formset_factory
from .models import ArchiveBox, ArchiveRoom, Cabinet, Slot, Archive

class ArchiveBoxForm(forms.ModelForm):
    archive_room = forms.ModelChoiceField(
        queryset=ArchiveRoom.objects.all(),
        label="档案室",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_archive_room'})
    )
    
    cabinet = forms.ModelChoiceField(
        queryset=Cabinet.objects.none(),
        label="柜子",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_cabinet'})
    )
    
    class Meta:
        model = ArchiveBox
        fields = ['name', 'document_number', 'date', 'description', 'is_special', 'project']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_special': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'project': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['document_number'].required = False
        self.fields['date'].required = False
        self.fields['description'].required = False
        
        # 如果有archive_room值，过滤cabinet选项
        if 'archive_room' in self.data:
            try:
                archive_room_id = int(self.data.get('archive_room'))
                self.fields['cabinet'].queryset = Cabinet.objects.filter(archive_room_id=archive_room_id)
            except (ValueError, TypeError):
                pass

class ArchiveForm(forms.ModelForm):
    class Meta:
        model = Archive
        exclude = ['box', 'import_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'copy_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'is_in_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['is_in_stock'].initial = True
        self.fields['pdf_file'].required = False
        self.fields['pdf_file'].widget.attrs.update({'class': 'form-control'})

# 创建一个档案表单集，初始显示5行，最多添加20行
ArchiveFormSet = formset_factory(ArchiveForm, extra=5, max_num=20)