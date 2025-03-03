from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.views import View

from .models import ArchiveRoom, Cabinet, Slot, Archive, ArchiveBox
from .forms import ArchiveForm, ArchiveSearchForm

def home(request):
    """档案管理首页"""
    rooms = ArchiveRoom.objects.all()
    return render(request, 'archives/home.html', {'rooms': rooms})

def cabinet_slots(request, cabinet_id):
    """显示柜子的格子占用情况"""
    cabinet = get_object_or_404(Cabinet, pk=cabinet_id)
    slots = Slot.objects.filter(cabinet=cabinet)
    
    # 预处理数据，创建一个二维网格
    left_grid = [[None for _ in range(cabinet.columns)] for _ in range(cabinet.rows)]
    right_grid = [[None for _ in range(cabinet.columns)] for _ in range(cabinet.rows)]
    
    for slot in slots:
        if slot.side == 'left':
            left_grid[slot.row-1][slot.column-1] = slot
        else:
            right_grid[slot.row-1][slot.column-1] = slot
    
    return render(request, 'archives/cabinet_slots.html', {
        'cabinet': cabinet,
        'left_grid': left_grid,
        'right_grid': right_grid,
    })

def get_available_slots(request):
    """API接口：获取可用的格子"""
    if request.method == 'GET':
        archive_room_id = request.GET.get('archive_room_id')
        cabinet_id = request.GET.get('cabinet_id')
        
        if cabinet_id:
            # 查询特定柜子的可用格子
            available_slots = Slot.objects.filter(
                cabinet_id=cabinet_id,
                is_occupied=False
            ).values('id', 'side', 'row', 'column')
            return JsonResponse({'slots': list(available_slots)})
            
        elif archive_room_id:
            # 返回档案室的所有柜子
            cabinets = Cabinet.objects.filter(
                archive_room_id=archive_room_id
            ).values('id', 'cabinet_number')
            return JsonResponse({'cabinets': list(cabinets)})
            
    return JsonResponse({'error': '参数错误'}, status=400)

class ArchiveCreateView(CreateView):
    """创建新档案"""
    model = Archive
    form_class = ArchiveForm
    template_name = 'archives/archive_form.html'
    success_url = reverse_lazy('archive_list')
    
    def form_valid(self, form):
        cabinet = form.cleaned_data['cabinet']
        side = form.cleaned_data['side']
        row = form.cleaned_data['row']
        column = form.cleaned_data['column']
        
        slot, created = Slot.objects.get_or_create(
            cabinet=cabinet,
            side=side,
            row=row,
            column=column,
            defaults={'is_occupied': False}
        )
        
        self.object = form.save(commit=False)
        self.object.slot = slot
        self.object.save()
        
        messages.success(self.request, f'档案 "{self.object.title}" 已成功创建')
        return redirect(self.success_url)

class ArchiveListView(ListView):
    """档案列表视图"""
    model = Archive
    template_name = 'archives/archive_list.html'
    context_object_name = 'archives'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Archive.objects.all()
        form = ArchiveSearchForm(self.request.GET)
        
        if form.is_valid():
            title = form.cleaned_data.get('title')
            cabinet_number = form.cleaned_data.get('cabinet_number')
            is_in_stock = form.cleaned_data.get('is_in_stock')
            
            if title:
                queryset = queryset.filter(title__icontains=title)
            
            if cabinet_number and cabinet_number.strip():
                queryset = queryset.filter(slot__cabinet__cabinet_number__icontains=cabinet_number)
                
            if is_in_stock is not None:
                queryset = queryset.filter(is_in_stock=is_in_stock)
                
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ArchiveSearchForm(self.request.GET)
        return context

class ArchiveDetailView(DetailView):
    """档案详情视图"""
    model = Archive
    template_name = 'archives/archive_detail.html'
    context_object_name = 'archive'

class PlaceArchiveBoxView(View):
    """放置档案盒到架子上"""
    
    def get(self, request):
        boxes = ArchiveBox.objects.all()  # 获取所有档案盒
        return render(request, 'archives/place_archive_box.html', {'boxes': boxes})

    def post(self, request):
        box_id = request.POST.get('box_id')
        # 这里可以添加逻辑将档案盒放置到架子上
        # ...
        return redirect('archive_list')  # 重定向到档案列表或其他页面