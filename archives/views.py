from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import ArchiveRoom, Cabinet, Slot, ArchiveBox
from .forms import ArchiveBoxForm

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