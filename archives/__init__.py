import os
from pathlib import Path

# 确保媒体目录存在
def ensure_media_dirs():
    # 获取当前项目根目录
    BASE_DIR = Path(__file__).resolve().parent.parent
    
    # 创建媒体目录
    media_root = os.path.join(BASE_DIR, 'media')
    pdfs_dir = os.path.join(media_root, 'archives', 'pdfs')
    
    if not os.path.exists(media_root):
        os.makedirs(media_root)
    
    if not os.path.exists(pdfs_dir):
        os.makedirs(pdfs_dir)

# 在应用程序启动时运行
ensure_media_dirs()
