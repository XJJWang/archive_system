from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.forms import formset_factory
from django.db import transaction
from django.utils import timezone
from datetime import datetime
from .models import ArchiveRoom, Cabinet, Slot, ArchiveBox, Archive
from .forms import ArchiveBoxForm, ArchiveForm, ArchiveFormSet

def home(request):
    """首页视图"""
    rooms = ArchiveRoom.objects.all().prefetch_related('cabinets', 'cabinets__slots')
    return render(request, 'archives/home.html', {
        'rooms': rooms
    })

def create_archive_box(request):
    """创建新档案盒视图"""
    if request.method == 'POST':
        form = ArchiveBoxForm(request.POST)
        if form.is_valid():
            # 创建档案盒但暂不保存
            archive_box = form.save(commit=False)
            
            # 获取所选格子
            slot_id = request.POST.get('slot')
            if slot_id:
                slot = get_object_or_404(Slot, id=slot_id)
                archive_box.slot = slot
            
            # 保存档案盒
            archive_box.save()
            
            messages.success(request, f'档案盒 "{archive_box.name}" 创建成功！')
            return redirect('home')
    else:
        form = ArchiveBoxForm()
    
    # 获取所有档案室
    archive_rooms = ArchiveRoom.objects.all()
    
    return render(request, 'archives/create_archive_box.html', {
        'form': form,
        'archive_rooms': archive_rooms,
    })

def load_cabinets(request):
    """AJAX加载柜子列表"""
    archive_room_id = request.GET.get('archive_room')
    cabinets = Cabinet.objects.filter(archive_room_id=archive_room_id).order_by('cabinet_number')
    return JsonResponse(list(cabinets.values('id', 'cabinet_number')), safe=False)

def load_slots(request):
    """AJAX加载可用格子列表"""
    cabinet_id = request.GET.get('cabinet')
    # 只获取未占用的格子
    slots = Slot.objects.filter(cabinet_id=cabinet_id, is_occupied=False).order_by('side', 'row', 'column')
    data = []
    for slot in slots:
        side_display = '左侧' if slot.side == 'left' else '右侧'
        slot_data = {
            'id': slot.id,
            'display': f"{side_display} 第{slot.row}排 第{slot.column}列"
        }
        data.append(slot_data)
    return JsonResponse(data, safe=False)


def add_archives(request):
    """批量添加档案视图"""
    # 获取最新添加的非特殊档案盒，按创建时间降序排序
    recent_boxes = ArchiveBox.objects.filter(is_special=False).order_by('-created_at')[:10]
    
    if request.method == 'POST':
        formset = ArchiveFormSet(request.POST)
        
        if formset.is_valid():
            # 获取选择的档案盒
            box_id = request.POST.get('archive_box')
            
            if not box_id:
                messages.error(request, '请选择档案盒')
                return render(request, 'archives/add_archives.html', {
                    'formset': formset,
                    'recent_boxes': recent_boxes,
                })
            
            try:
                box = ArchiveBox.objects.get(id=box_id)
                
                # 使用事务确保所有档案要么全部添加成功，要么全部失败
                with transaction.atomic():
                    added_count = 0
                    
                    for form in formset:
                        # 只处理填写了内容的表单
                        if form.cleaned_data and form.cleaned_data.get('title'):
                            archive = form.save(commit=False)
                            archive.box = box
                            
                            # 如果没有设置入库时间，使用档案盒的日期或当前时间
                            if not archive.import_date:
                                if box.date:
                                    archive.import_date = datetime.combine(box.date, datetime.min.time())
                                else:
                                    archive.import_date = timezone.now()
                            
                            archive.save()
                            added_count += 1
                    
                    if added_count > 0:
                        if added_count == 1:
                            messages.success(request, f'成功添加1份档案到"{box.name}"')
                        else:
                            messages.success(request, f'成功添加{added_count}份档案到"{box.name}"')
                        return redirect('/')
                    else:
                        messages.warning(request, '未添加任何档案，请填写至少一份档案信息')
                
            except ArchiveBox.DoesNotExist:
                messages.error(request, '选择的档案盒不存在')
        else:
            messages.error(request, '表单数据有误，请检查后重新提交')
    else:
        formset = ArchiveFormSet()
    
    return render(request, 'archives/add_archives.html', {
        'formset': formset,
        'recent_boxes': recent_boxes,
    })