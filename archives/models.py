from django.db import models

# Create your models here.

class ArchiveRoom(models.Model):
    """档案室模型"""
    name = models.CharField(max_length=100, verbose_name="档案室名称")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "档案室"
        verbose_name_plural = "档案室"
        
    def __str__(self):
        return self.name


class Cabinet(models.Model):
    """柜子模型"""
    archive_room = models.ForeignKey(ArchiveRoom, on_delete=models.CASCADE, related_name="cabinets", verbose_name="所属档案室")
    cabinet_number = models.CharField(max_length=50, verbose_name="柜子编号")
    rows = models.PositiveIntegerField(default=5, verbose_name="行数")
    columns = models.PositiveIntegerField(default=5, verbose_name="列数")
    
    class Meta:
        verbose_name = "柜子"
        verbose_name_plural = "柜子"
        
    def __str__(self):
        return f"{self.archive_room.name} - 柜子 {self.cabinet_number}"


class Slot(models.Model):
    """格子模型"""
    SIDE_CHOICES = [
        ('left', '左侧'),
        ('right', '右侧'),
    ]
    
    cabinet = models.ForeignKey(Cabinet, on_delete=models.CASCADE, related_name="slots", verbose_name="所属柜子")
    side = models.CharField(max_length=5, choices=SIDE_CHOICES, verbose_name="侧面")
    row = models.PositiveIntegerField(verbose_name="行号")
    column = models.PositiveIntegerField(verbose_name="列号")
    is_occupied = models.BooleanField(default=False, verbose_name="是否已占用")
    
    class Meta:
        verbose_name = "格子"
        verbose_name_plural = "格子"
        unique_together = ['cabinet', 'side', 'row', 'column']
        
    def __str__(self):
        return f"{self.cabinet} - {self.get_side_display()} [{self.row}, {self.column}]"


class ArchiveBox(models.Model):
    """档案盒模型"""
    name = models.CharField(max_length=100, verbose_name="名称")
    document_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="文档号")
    date = models.DateField(blank=True, null=True, verbose_name="日期")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    slot = models.ForeignKey(Slot, on_delete=models.SET_NULL, null=True, blank=True, related_name="archive_boxes", verbose_name="所在格子")
    is_special = models.BooleanField(default=False, verbose_name="是否特殊项目")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name="archive_boxes", verbose_name="所属项目")
    
    class Meta:
        verbose_name = "档案盒"
        verbose_name_plural = "档案盒"
        
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # 保存前先检查旧的slot位置
        if self.pk:
            try:
                old_box = ArchiveBox.objects.get(pk=self.pk)
                old_slot = old_box.slot
                if old_slot and old_slot != self.slot:
                    # 释放旧位置
                    old_slot.is_occupied = False
                    old_slot.save()
            except ArchiveBox.DoesNotExist:
                pass
        
        # 更新新位置的占用状态
        if self.slot:
            self.slot.is_occupied = True
            self.slot.save()
            
        super().save(*args, **kwargs)
    
    def get_location_description(self):
        """获取档案盒位置描述"""
        if not self.slot:
            return "未放置"
        side_display = '左侧' if self.slot.side == 'left' else '右侧'
        return f"{self.slot.cabinet.cabinet_number}号柜子{side_display}第{self.slot.row}排第{self.slot.column}列"


class Archive(models.Model):
    """档案模型"""
    title = models.CharField(max_length=200, verbose_name="标题")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    box = models.ForeignKey(ArchiveBox, on_delete=models.CASCADE, related_name="archives", verbose_name="所属档案盒")
    import_date = models.DateTimeField(auto_now_add=True, verbose_name="入库时间")
    copy_count = models.PositiveIntegerField(default=1, verbose_name="份数")
    is_in_stock = models.BooleanField(default=True, verbose_name="是否在库中")
    pdf_file = models.FileField(upload_to='archives/pdfs/%Y/%m/', blank=True, null=True, verbose_name="PDF扫描件")
    
    class Meta:
        verbose_name = "档案"
        verbose_name_plural = "档案"
        
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @classmethod
    def find_by_location(cls, cabinet_number, side, row, column):
        """通过位置查找档案"""
        try:
            slot = Slot.objects.get(
                cabinet__cabinet_number=cabinet_number,
                side=side,
                row=row,
                column=column
            )
            return cls.objects.filter(slot=slot).first()
        except Slot.DoesNotExist:
            return None            
    def get_location_description(self):
        """获取档案位置描述"""
        if not self.box or not self.box.slot:
            return "未放置"
        slot = self.box.slot
        side_display = '左侧' if slot.side == 'left' else '右侧'
        return f"{slot.cabinet.cabinet_number}号柜子{side_display}第{slot.row}排第{slot.column}列"


class Project(models.Model):
    """项目模型"""
    name = models.CharField(max_length=200, verbose_name="项目名称")
    short_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="项目简称")
    year = models.IntegerField(verbose_name="年份")
    information = models.TextField(blank=True, null=True, verbose_name="基本信息")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    
    class Meta:
        verbose_name = "项目"
        verbose_name_plural = "项目"
        ordering = ['-year', 'name']
        
    def __str__(self):
        if self.short_name:
            return f"{self.short_name} ({self.year})"
        return f"{self.name} ({self.year})"
