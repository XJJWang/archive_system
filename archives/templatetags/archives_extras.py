from django import template

register = template.Library()

@register.filter
def to(start, end):
    """用法：1|to:6，返回[1,2,3,4,5,6]"""
    return range(int(start), int(end)+1)

@register.filter
def get_slot(slots, row_col):
    """
    用法：slots|get_slot:'row,col'
    容错处理，避免row或col为None时报错
    """
    slots = list(slots)  # 强制转为list，避免QuerySet惰性问题
    print(f"【get_slot调试】slots数量={len(slots)}, row_col={row_col}")
    if not row_col or ',' not in str(row_col):
        return None
    try:
        row, col = map(int, str(row_col).split(','))
    except Exception:
        return None
    for slot in slots:
        if int(slot.row) == row and int(slot.column) == col:
            print(f"【get_slot调试】找到slot: pk={slot.pk}, row={slot.row}, col={slot.column}")
            return slot
    print(f"【get_slot调试】未找到slot: row={row}, col={col}")
    return None