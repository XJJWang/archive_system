from django.shortcuts import render
from django.db.models import Q
from archives.models import Archive, Project

# Create your views here.

def search(request):
    """处理档案搜索请求"""
    # 获取所有项目数据
    projects = Project.objects.all().order_by('-year', 'name')
    
    # 获取项目年份列表（去重）
    project_years = Project.objects.values_list('year', flat=True).distinct().order_by('-year')
    
    # 初始化查询集
    archives = Archive.objects.all()
    
    # 提取搜索参数
    query = request.GET.get('q', '')
    project_id = request.GET.get('project', '')
    year = request.GET.get('year', '')
    status = request.GET.get('status', '')
    
    # 记录是否提交了搜索
    search_submitted = any([query, project_id, year, status])
    
    # 应用搜索和筛选条件
    if search_submitted:
        # 关键词搜索
        if query:
            archives = archives.filter(
                Q(title__icontains=query) | 
                Q(description__icontains=query) | 
                Q(box__document_number__icontains=query)
            )
        
        # 按项目筛选
        if project_id:
            archives = archives.filter(box__project_id=project_id)
        
        # 按项目年份筛选 - 注意这里是项目的年份，不是档案的导入日期
        if year:
            archives = archives.filter(box__project__year=year)
        
        # 按档案状态筛选
        if status == 'available':
            archives = archives.filter(is_in_stock=True)
        elif status == 'borrowed':
            archives = archives.filter(is_in_stock=False)
        
        # 获取最终结果集
        archives = archives.select_related('box', 'box__project').order_by('-import_date')[:100]
    else:
        # 无搜索条件时不返回结果
        archives = Archive.objects.none()
    
    # 构建上下文变量
    context = {
        'projects': projects,
        'project_years': project_years,
        'search_results': archives,
        'search_submitted': search_submitted,
        'query': query,
        'selected_project': project_id,
        'selected_year': year,
        'selected_status': status,
        'result_count': archives.count(),
    }
    
    return render(request, 'borrow/home.html', context)

def home(request):
    """首页视图"""
    # 获取项目列表
    projects = Project.objects.all().order_by('-year', 'name')
    
    # 获取项目年份列表（去重）
    project_years = Project.objects.values_list('year', flat=True).distinct().order_by('-year')
    
    return render(request, 'borrow/home.html', {
        'projects': projects,
        'project_years': project_years,
        'search_submitted': False
    })
