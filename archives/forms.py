from django import forms
from django.forms import widgets
from .models import ArchiveBox, ArchiveRoom, Cabinet, Slot

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
        fields = ['name', 'document_number', 'date', 'description', 'is_special']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_special': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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