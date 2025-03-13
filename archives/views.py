from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.forms import formset_factory
from django.db import transaction
from .models import ArchiveRoom, Cabinet, Slot, ArchiveBox, Archive, Project
from .forms import ArchiveBoxForm, ArchiveForm, ArchiveFormSet
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group


@login_required(login_url='archives:login')
@permission_required('borrow.can_manage_archives', login_url='archives:login', raise_exception=True)
def home(request):
    """首页视图"""
    rooms = ArchiveRoom.objects.all().prefetch_related('cabinets', 'cabinets__slots')
    return render(request, 'archives/home.html', {
        'rooms': rooms
    })

def archives_login(request):
    """档案管理系统登录视图"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # 检查用户是否是档案室管理员
            print(user.groups)
            if user.groups.filter(name='档案室管理员').exists():
                login(request, user)
                return redirect('archives:home')
            else:
                messages.error(request, '您没有权限访问档案管理系统')
        else:
            messages.error(request, '用户名或密码不正确')
    
    return render(request, 'archives/login.html')

def archives_logout(request):
    """档案管理系统登出"""
    logout(request)
    return redirect('archives:login')


@login_required(login_url='archives:login')
@permission_required('borrow.can_manage_archives', login_url='archives:login', raise_exception=True)
def create_archive_box(request):
    """创建新档案盒"""
    initial_data = {}
    
    # 如果URL中包含project参数，预选项目
    project_id = request.GET.get('project')
    if project_id:
        try:
            project = Project.objects.get(id=project_id)
            initial_data['project'] = project.id
        except (Project.DoesNotExist, ValueError):
            pass
    
    if request.method == 'POST':
        form = ArchiveBoxForm(request.POST)
        if form.is_valid():
            # 确保project是有效的ID或对象
            if not form.cleaned_data.get('project'):
                # 如果没有选择项目，返回错误
                form.add_error('project', '必须选择一个项目')
            else:
                archive_box = form.save(commit=False)
                
                # 处理位置信息
                slot_id = request.POST.get('slot')
                if slot_id:
                    try:
                        slot = Slot.objects.get(id=slot_id)
                        archive_box.slot = slot
                    except (Slot.DoesNotExist, ValueError):
                        # 处理无效的slot_id
                        pass
                
                archive_box.save()
                messages.success(request, f'档案盒 "{archive_box.name}" 创建成功！')
                return redirect('archives:archive_box_detail', pk=archive_box.pk)
    else:
        form = ArchiveBoxForm(initial=initial_data)
    
    return render(request, 'archives/create_archive_box.html', {
        'form': form,
    })


@login_required(login_url='archives:login')
@permission_required('borrow.can_manage_archives', login_url='archives:login', raise_exception=True)
def load_cabinets(request):
    """AJAX加载柜子列表"""
    archive_room_id = request.GET.get('archive_room')
    cabinets = Cabinet.objects.filter(archive_room_id=archive_room_id).order_by('cabinet_number')
    return JsonResponse(list(cabinets.values('id', 'cabinet_number')), safe=False)


@login_required(login_url='archives:login')
@permission_required('borrow.can_manage_archives', login_url='archives:login', raise_exception=True)
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


@login_required(login_url='archives:login')
@permission_required('borrow.can_manage_archives', login_url='archives:login', raise_exception=True)
def add_archives(request):
    """批量添加档案视图"""
    # 获取最新添加的非特殊档案盒，按创建时间降序排序
    recent_boxes = ArchiveBox.objects.filter(is_special=False).order_by('-created_at')[:10]
    
    # 预选档案盒（如果从URL参数中提供）
    selected_box_id = request.GET.get('box')
    selected_box = None
    if selected_box_id:
        try:
            selected_box = ArchiveBox.objects.get(id=selected_box_id)
        except (ArchiveBox.DoesNotExist, ValueError):
            pass
    
    if request.method == 'POST':
        formset = ArchiveFormSet(request.POST, request.FILES)
        
        if formset.is_valid():
            # 获取选择的档案盒
            box_id = request.POST.get('archive_box')
            
            if not box_id:
                messages.error(request, '请选择档案盒')
                return render(request, 'archives/add_archives.html', {
                    'formset': formset,
                    'recent_boxes': recent_boxes,
                    'selected_box': selected_box,
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
                            
                            # 处理PDF文件上传（如果有）
                            if 'pdf_file' in form.files:
                                archive.pdf_file = form.files['pdf_file']
                                
                            archive.save()
                            added_count += 1
                    
                    if added_count > 0:
                        if added_count == 1:
                            messages.success(request, f'成功添加1份档案到"{box.name}"')
                        else:
                            messages.success(request, f'成功添加{added_count}份档案到"{box.name}"')
                        return redirect('archives:archive_box_detail', pk=box.pk)
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
        'selected_box': selected_box,
    })


@login_required(login_url='archives:login')
@permission_required('borrow.can_manage_archives', login_url='archives:login', raise_exception=True)
def project_list(request):
    """项目列表视图"""
    projects = Project.objects.all().order_by('-year', 'name')
    current_year = datetime.now().year
    return render(request, 'archives/project_list.html', {
        'projects': projects,
        'current_year': current_year
    })


@login_required(login_url='archives:login')
@permission_required('borrow.can_manage_archives', login_url='archives:login', raise_exception=True)
def project_detail(request, pk):
    """项目详情视图"""
    project = get_object_or_404(Project, pk=pk)
    archive_boxes = project.archive_boxes.all().order_by('-created_at')
    return render(request, 'archives/project_detail.html', {
        'project': project,
        'archive_boxes': archive_boxes
    })


@login_required(login_url='archives:login')
@permission_required('borrow.can_manage_archives', login_url='archives:login', raise_exception=True)
def create_project(request):
    """创建新项目"""
    if request.method == 'POST':
        name = request.POST.get('name')
        short_name = request.POST.get('short_name', '')
        year = request.POST.get('year')
        information = request.POST.get('information', '')
        
        if not name or not year:
            messages.error(request, '项目名称和年份不能为空')
            return redirect('archives:project_list')
        
        try:
            year = int(year)
        except ValueError:
            messages.error(request, '年份必须是数字')
            return redirect('archives:project_list')
        
        project = Project.objects.create(
            name=name,
            short_name=short_name if short_name else None,
            year=year,
            information=information
        )
        
        messages.success(request, f'项目 "{project.name}" 创建成功！')
        return redirect('archives:project_detail', pk=project.id)
    
    return redirect('archives:project_list')


@login_required(login_url='archives:login')
@permission_required('borrow.can_manage_archives', login_url='archives:login', raise_exception=True)
def initialize_cabinets(request):
    """初始化柜子和格子"""
    # 获取唯一的档案室
    try:
        archive_room = ArchiveRoom.objects.first()
        if not archive_room:
            messages.error(request, '没有找到档案室，请先创建档案室')
            return redirect('archives:home')
            
        # 获取当前柜子数量
        existing_cabinets = Cabinet.objects.filter(archive_room=archive_room).count()
        
        # 添加10个柜子
        cabinets_created = 0
        slots_created = 0
        
        for i in range(1, 11):
            cabinet_number = f"{existing_cabinets + i:02d}"
            cabinet, created = Cabinet.objects.get_or_create(
                archive_room=archive_room,
                cabinet_number=cabinet_number,
                defaults={
                    'rows': 6,
                    'columns': 5
                }
            )
            
            if created:
                cabinets_created += 1
                
                # 为每个柜子创建格子（左侧和右侧）
                for side in ['left', 'right']:
                    for row in range(1, 7):  # 6行
                        for col in range(1, 6):  # 5列
                            slot, slot_created = Slot.objects.get_or_create(
                                cabinet=cabinet,
                                side=side,
                                row=row,
                                column=col,
                                defaults={'is_occupied': False}
                            )
                            if slot_created:
                                slots_created += 1
        
        if cabinets_created > 0:
            messages.success(request, f'成功创建{cabinets_created}个柜子和{slots_created}个格子')
        else:
            messages.info(request, '柜子已存在，没有新建柜子')
            
        return redirect('archives:home')
        
    except Exception as e:
        messages.error(request, f'初始化柜子时出错: {str(e)}')
        return redirect('archives:home')


@login_required(login_url='archives:login')
@permission_required('borrow.can_manage_archives', login_url='archives:login', raise_exception=True)
def edit_project(request, pk):
    """编辑项目信息"""
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        short_name = request.POST.get('short_name', '')
        year = request.POST.get('year')
        information = request.POST.get('information', '')
        
        if not name or not year:
            messages.error(request, '项目名称和年份不能为空')
            # 获取Referer，以确定用户来自哪个页面
            referer = request.META.get('HTTP_REFERER', '')
            if 'projects/' in referer and not f'projects/{pk}' in referer:
                # 如果来自项目列表页
                return redirect('archives:project_list')
            # 否则，返回项目详情页
            return redirect('archives:project_detail', pk=project.pk)
        
        try:
            year = int(year)
        except ValueError:
            messages.error(request, '年份必须是数字')
            # 获取Referer，以确定用户来自哪个页面
            referer = request.META.get('HTTP_REFERER', '')
            if 'projects/' in referer and not f'projects/{pk}' in referer:
                # 如果来自项目列表页
                return redirect('archives:project_list')
            # 否则，返回项目详情页
            return redirect('archives:project_detail', pk=project.pk)
        
        # 更新项目信息
        project.name = name
        project.short_name = short_name if short_name else None
        project.year = year
        project.information = information
        project.save()
        
        messages.success(request, f'项目 "{project.name}" 更新成功！')
        
        # 获取Referer，以确定用户来自哪个页面
        referer = request.META.get('HTTP_REFERER', '')
        if 'projects/' in referer and not f'projects/{pk}' in referer:
            # 如果来自项目列表页
            return redirect('archives:project_list')
        # 否则，返回项目详情页
        return redirect('archives:project_detail', pk=project.pk)
    
    # 对于GET请求，重定向到项目详情页
    return redirect('archives:project_detail', pk=project.pk)

@login_required(login_url='archives:login')
@permission_required('borrow.can_manage_archives', login_url='archives:login', raise_exception=True)
def archive_box_detail(request, pk):
    """档案盒详情视图"""
    archive_box = get_object_or_404(ArchiveBox, pk=pk)
    archives = archive_box.archives.all().order_by('-import_date')
    
    return render(request, 'archives/archive_box_detail.html', {
        'box': archive_box,
        'archives': archives,
    })