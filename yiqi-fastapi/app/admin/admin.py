from typing import Any, Dict, List, Optional, Sequence, Union
from starlette_admin.contrib.sqla import Admin, ModelView
from starlette_admin.auth import AdminConfig, AdminUser, AuthProvider
from starlette_admin.exceptions import LoginFailed
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database import SessionLocal, engine
from app.models.user import UserProfile
from app.models.activity import Activity, ActivityType, ActivityImage, Slide
from app.models.social import ActivityUserInfo, CollectionUser, SharingUser, ReportUser, BrowseUser, Comment, Feedback
from app.models.message import SysUser, SysUserMenu, SysMessage
from app.models.sharing import SharingSet

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UsernamePasswordProvider(AuthProvider):
    """用户名密码认证提供者"""
    
    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request,
        response: Response,
    ) -> Response:
        db = SessionLocal()
        try:
            # 查找管理员用户
            user = db.query(UserProfile).filter(
                UserProfile.mobile == username,
                UserProfile.is_admin == True
            ).first()
            
            if not user or not user.hashed_password or not pwd_context.verify(password, user.hashed_password):
                raise LoginFailed("用户名或密码错误")
            
            # 设置session
            request.session.update({"user_id": user.id, "username": user.name})
            return response
        finally:
            db.close()

    async def is_authenticated(self, request: Request) -> bool:
        """检查用户是否已认证"""
        return "user_id" in request.session

    def get_admin_config(self, request: Request) -> AdminConfig:
        """获取admin配置"""
        return AdminConfig(
            app_title="天域同途管理系统",
        )

    def get_admin_user(self, request: Request) -> AdminUser:
        """获取admin用户信息"""
        username = request.session.get("username", "管理员")
        return AdminUser(username=username)

    async def logout(self, request: Request, response: Response) -> Response:
        """登出"""
        request.session.clear()
        return response


class SQLAlchemyModelView(ModelView):
    """SQLAlchemy模型视图基类"""
    
    def __init__(self, model, **kwargs):
        super().__init__(model, **kwargs)
        self.pk_attr = "id"  # 主键字段名


# 用户管理视图
class UserAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__(UserProfile)
        self.identity = "user"
        self.name = "用户管理"
        self.label = "用户管理"
        self.icon = "fa fa-users"
        
        # 搜索字段
        self.searchable_fields = ["name", "nick_name", "mobile"]
        
        # 排序字段
        self.sortable_fields = ["name", "mobile", "created_at"]
        
        # 默认排序
        self.fields_default_sort = [("created_at", True)]  # 按创建时间降序
        
        # 列表页排除字段
        self.exclude_fields_from_list = ["hashed_password", "openid", "user_bh", "avatar_url", "background"]
        
        # 详情页排除字段
        self.exclude_fields_from_detail = ["hashed_password", "openid"]
        
        # 创建页排除字段
        self.exclude_fields_from_create = ["hashed_password", "created_at", "updated_at"]
        
        # 编辑页排除字段
        self.exclude_fields_from_edit = ["hashed_password", "created_at", "updated_at"]
        
        # 分页设置
        self.page_size = 25
        self.page_size_options = [10, 25, 50, 100]


# 活动类型管理视图
class ActivityTypeAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__(ActivityType)
        self.identity = "activity_type"
        self.name = "活动类型"
        self.label = "活动类型"
        self.icon = "fa fa-tags"
        
        self.searchable_fields = ["name", "introduction"]
        self.sortable_fields = ["name", "index_num", "created_at"]
        self.fields_default_sort = [("index_num", False)]  # 按排序号升序
        self.page_size = 25


# 活动管理视图
class ActivityAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__(Activity)
        self.identity = "activity"
        self.name = "活动管理"
        self.label = "活动管理"
        self.icon = "fa fa-calendar"
        
        self.searchable_fields = ["title", "content", "address"]
        self.sortable_fields = ["title", "start_date", "created_at", "audit"]
        self.fields_default_sort = [("created_at", True)]  # 按创建时间倒序
        self.page_size = 25


# 分享设置管理视图
class SharingSetAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__(SharingSet)
        self.identity = "sharing_set"
        self.name = "分享设置"
        self.label = "分享设置"
        self.icon = "fa fa-share-alt"
        
        self.searchable_fields = ["title"]
        self.sortable_fields = ["title", "page_type", "created_at"]
        self.fields_default_sort = [("created_at", True)]  # 按创建时间降序
        self.page_size = 25


# 用户收藏管理视图
class UserCollectionAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__(CollectionUser)
        self.identity = "user_collection"
        self.name = "用户收藏"
        self.label = "用户收藏"
        self.icon = "fa fa-star"
        
        self.sortable_fields = ["created_at"]
        self.fields_default_sort = [("created_at", True)]
        self.page_size = 25


# 举报管理视图
class UserReportAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__(ReportUser)
        self.identity = "user_report"
        self.name = "举报管理"
        self.label = "举报管理"
        self.icon = "fa fa-exclamation-triangle"
        
        self.searchable_fields = ["reason"]
        self.sortable_fields = ["created_at"]
        self.fields_default_sort = [("created_at", True)]
        self.page_size = 25


# 评论管理视图
class CommentAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__(Comment)
        self.identity = "comment"
        self.name = "评论管理"
        self.label = "评论管理"
        self.icon = "fa fa-comments"
        
        self.searchable_fields = ["content"]
        self.sortable_fields = ["created_at"]
        self.fields_default_sort = [("created_at", True)]
        self.page_size = 25


# 反馈管理视图
class FeedbackAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__(Feedback)
        self.identity = "feedback"
        self.name = "反馈管理"
        self.label = "反馈管理"
        self.icon = "fa fa-envelope"
        
        self.searchable_fields = ["title", "content"]
        self.sortable_fields = ["created_at", "is_handled"]
        self.fields_default_sort = [("created_at", True)]
        self.page_size = 25


# 活动报名管理视图
class ActivityUserInfoAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__(ActivityUserInfo)
        self.identity = "activity_user_info"
        self.name = "活动报名"
        self.label = "活动报名"
        self.icon = "fa fa-users"
        
        self.searchable_fields = ["username", "wechat"]
        self.sortable_fields = ["created_at", "user_type"]
        self.fields_default_sort = [("created_at", True)]
        self.page_size = 25


# 系统用户管理视图
class SysUserAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__(SysUser)
        self.identity = "sys_user"
        self.name = "系统用户"
        self.label = "系统用户"
        self.icon = "fa fa-cog"
        
        self.searchable_fields = ["name", "introduction"]
        self.sortable_fields = ["name", "created_at"]
        self.fields_default_sort = [("created_at", True)]  # 按创建时间降序
        self.page_size = 25


# 系统消息管理视图
class SystemMessageAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__(SysMessage)
        self.identity = "sys_message"
        self.name = "系统消息"
        self.label = "系统消息"
        self.icon = "fa fa-bell"
        
        self.searchable_fields = ["title", "content"]
        self.sortable_fields = ["created_at", "status"]
        self.fields_default_sort = [("created_at", True)]
        self.page_size = 25


# 创建Admin实例 - 使用SQLAlchemy集成
admin = Admin(
    engine=engine,
    title="天域同途管理系统",
    base_url="/admin",
    auth_provider=UsernamePasswordProvider(),
    debug=True
)

# 注册视图
admin.add_view(UserAdmin())
admin.add_view(ActivityTypeAdmin())
admin.add_view(ActivityAdmin())
admin.add_view(ActivityUserInfoAdmin())
admin.add_view(SharingSetAdmin())
admin.add_view(UserCollectionAdmin())
admin.add_view(UserReportAdmin())
admin.add_view(CommentAdmin())
admin.add_view(FeedbackAdmin())
admin.add_view(SysUserAdmin())
admin.add_view(SystemMessageAdmin())