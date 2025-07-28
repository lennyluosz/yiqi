import os
import uuid
from typing import Optional, List
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import magic
from datetime import datetime

from app.config import settings


class FileUploadService:
    """文件上传服务"""
    
    # 允许的图片格式
    ALLOWED_IMAGE_TYPES = {
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'
    }
    
    # 允许的文件格式
    ALLOWED_FILE_TYPES = {
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp',
        'application/pdf', 'text/plain', 'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    
    def __init__(self):
        # 确保上传目录存在
        os.makedirs(settings.upload_dir, exist_ok=True)
        
        # 创建子目录
        self.image_dir = os.path.join(settings.upload_dir, "images")
        self.document_dir = os.path.join(settings.upload_dir, "documents")
        self.avatar_dir = os.path.join(settings.upload_dir, "avatars")
        self.activity_dir = os.path.join(settings.upload_dir, "activities")
        
        for directory in [self.image_dir, self.document_dir, self.avatar_dir, self.activity_dir]:
            os.makedirs(directory, exist_ok=True)

    def validate_file(self, file: UploadFile, file_types: set = None) -> bool:
        """验证文件"""
        if file_types is None:
            file_types = self.ALLOWED_FILE_TYPES
            
        # 检查文件大小
        if file.size and file.size > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"文件大小超过限制 ({settings.max_file_size / 1024 / 1024:.1f}MB)"
            )
        
        # 检查文件类型
        if file.content_type not in file_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的文件类型: {file.content_type}"
            )
        
        return True

    def generate_filename(self, original_filename: str, prefix: str = "") -> str:
        """生成唯一文件名"""
        # 获取文件扩展名
        _, ext = os.path.splitext(original_filename)
        
        # 生成唯一ID
        unique_id = uuid.uuid4().hex
        
        # 添加时间戳
        timestamp = datetime.now().strftime("%Y%m%d")
        
        # 组合文件名
        if prefix:
            filename = f"{prefix}_{timestamp}_{unique_id}{ext}"
        else:
            filename = f"{timestamp}_{unique_id}{ext}"
        
        return filename

    def get_file_path(self, category: str, filename: str) -> str:
        """获取文件保存路径"""
        category_dirs = {
            "image": self.image_dir,
            "avatar": self.avatar_dir,
            "activity": self.activity_dir,
            "document": self.document_dir
        }
        
        base_dir = category_dirs.get(category, self.image_dir)
        
        # 按年月创建子目录
        year_month = datetime.now().strftime("%Y/%m")
        full_dir = os.path.join(base_dir, year_month)
        os.makedirs(full_dir, exist_ok=True)
        
        return os.path.join(full_dir, filename)

    def get_url_path(self, file_path: str) -> str:
        """获取文件的URL路径"""
        # 移除upload_dir前缀，返回相对路径
        relative_path = os.path.relpath(file_path, settings.upload_dir)
        return f"/static/{relative_path.replace(os.sep, '/')}"

    async def save_file(
        self, 
        file: UploadFile, 
        category: str = "image",
        prefix: str = "",
        allowed_types: set = None
    ) -> str:
        """保存文件并返回URL路径"""
        # 验证文件
        self.validate_file(file, allowed_types or self.ALLOWED_FILE_TYPES)
        
        # 生成文件名
        filename = self.generate_filename(file.filename, prefix)
        
        # 获取保存路径
        file_path = self.get_file_path(category, filename)
        
        # 保存文件
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"文件保存失败: {str(e)}"
            )
        
        # 如果是图片，进行处理
        if file.content_type in self.ALLOWED_IMAGE_TYPES:
            self.process_image(file_path)
        
        return self.get_url_path(file_path)

    def process_image(self, file_path: str, max_size: tuple = (1920, 1080)) -> None:
        """处理图片：压缩、调整大小等"""
        try:
            with Image.open(file_path) as img:
                # 转换RGBA为RGB（如果需要）
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # 调整图片大小
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # 保存压缩后的图片
                img.save(file_path, optimize=True, quality=85)
                
        except Exception as e:
            # 如果图片处理失败，记录错误但不中断流程
            print(f"图片处理失败: {str(e)}")

    async def save_multiple_files(
        self, 
        files: List[UploadFile], 
        category: str = "image",
        prefix: str = "",
        allowed_types: set = None
    ) -> List[str]:
        """批量保存文件"""
        file_urls = []
        
        for file in files:
            try:
                url = await self.save_file(file, category, prefix, allowed_types)
                file_urls.append(url)
            except Exception as e:
                # 记录错误但继续处理其他文件
                print(f"文件 {file.filename} 上传失败: {str(e)}")
                continue
        
        return file_urls

    def delete_file(self, file_url: str) -> bool:
        """删除文件"""
        try:
            # 从URL路径转换为文件系统路径
            if file_url.startswith("/static/"):
                relative_path = file_url[8:]  # 移除 "/static/" 前缀
                file_path = os.path.join(settings.upload_dir, relative_path.replace("/", os.sep))
                
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return True
            
            return False
            
        except Exception as e:
            print(f"删除文件失败: {str(e)}")
            return False

    def get_file_info(self, file_path: str) -> dict:
        """获取文件信息"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            file_type = magic.from_file(file_path, mime=True)
            
            info = {
                "size": stat.st_size,
                "type": file_type,
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime)
            }
            
            # 如果是图片，获取尺寸信息
            if file_type in self.ALLOWED_IMAGE_TYPES:
                try:
                    with Image.open(file_path) as img:
                        info["width"] = img.width
                        info["height"] = img.height
                except:
                    pass
            
            return info
            
        except Exception as e:
            print(f"获取文件信息失败: {str(e)}")
            return None


# 创建全局文件上传服务实例
file_upload_service = FileUploadService()