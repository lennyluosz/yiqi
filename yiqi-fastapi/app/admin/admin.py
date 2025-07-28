from typing import Any, Dict, List, Optional, Sequence, Union
from starlette_admin import BaseAdmin, BaseModelView
from starlette_admin.auth import AdminConfig, AdminUser, AuthProvider
from starlette_admin.exceptions import LoginFailed
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
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
            app_title="一起呦管理系统",
        )

    def get_admin_user(self, request: Request) -> AdminUser:
        """获取admin用户信息"""
        username = request.session.get("username", "管理员")
        return AdminUser(username=username)

    async def logout(self, request: Request, response: Response) -> Response:
        """登出"""
        request.session.clear()
        return response


class SQLAlchemyModelView(BaseModelView):
    """SQLAlchemy模型视图基类"""
    model = None
    
    def __init__(self):
        super().__init__()
        self.pk_attr = "id"  # 主键字段名
    
    async def count(
        self,
        request: Request,
        where: Union[Dict[str, Any], str, None] = None,
    ) -> int:
        """统计记录数"""
        db = SessionLocal()
        try:
            query = db.query(self.model)
            if where:
                query = self._apply_where_clause(query, where)
            return query.count()
        finally:
            db.close()
    
    async def find_all(
        self,
        request: Request,
        skip: int = 0,
        limit: int = 100,
        where: Union[Dict[str, Any], str, None] = None,
        order_by: Optional[List[str]] = None,
    ) -> Sequence[Any]:
        """查找所有记录"""
        db = SessionLocal()
        try:
            query = db.query(self.model)
            
            # 应用where条件
            if where:
                query = self._apply_where_clause(query, where)
            
            # 应用排序
            if order_by:
                query = self._apply_order_by(query, order_by)
            
            # 应用分页
            return query.offset(skip).limit(limit).all()
        finally:
            db.close()
    
    async def find_by_pk(self, request: Request, pk: Any) -> Optional[Any]:
        """按主键查找记录"""
        db = SessionLocal()
        try:
            return db.query(self.model).filter(getattr(self.model, self.pk_attr) == pk).first()
        finally:
            db.close()
    
    async def find_by_pks(self, request: Request, pks: List[Any]) -> Sequence[Any]:
        """按多个主键查找记录"""
        db = SessionLocal()
        try:
            return db.query(self.model).filter(getattr(self.model, self.pk_attr).in_(pks)).all()
        finally:
            db.close()
    
    async def create(self, request: Request, data: Dict[str, Any]) -> Any:
        """创建记录"""
        db = SessionLocal()
        try:
            # 过滤掉空值和不存在的字段
            filtered_data = {}
            for key, value in data.items():
                if hasattr(self.model, key) and value is not None:
                    filtered_data[key] = value
            
            obj = self.model(**filtered_data)
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    async def edit(self, request: Request, pk: Any, data: Dict[str, Any]) -> Any:
        """编辑记录"""
        db = SessionLocal()
        try:
            obj = db.query(self.model).filter(getattr(self.model, self.pk_attr) == pk).first()
            if not obj:
                return None
            
            # 更新字段
            for key, value in data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            
            db.commit()
            db.refresh(obj)
            return obj
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    async def delete(self, request: Request, pks: List[Any]) -> Optional[int]:
        """删除记录"""
        db = SessionLocal()
        try:
            count = db.query(self.model).filter(getattr(self.model, self.pk_attr).in_(pks)).count()
            db.query(self.model).filter(getattr(self.model, self.pk_attr).in_(pks)).delete(synchronize_session=False)
            db.commit()
            return count
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def _apply_where_clause(self, query, where):
        """应用where条件"""
        if isinstance(where, str):
            # 简单文本搜索
            return self._apply_text_search(query, where)
        elif isinstance(where, dict):
            # 复杂查询条件
            return self._apply_dict_where(query, where)
        return query
    
    def _apply_text_search(self, query, text):
        """应用文本搜索"""
        if not hasattr(self, 'searchable_fields') or not self.searchable_fields:
            return query
        
        conditions = []
        for field in self.searchable_fields:
            if hasattr(self.model, field):
                attr = getattr(self.model, field)
                conditions.append(attr.contains(text))
        
        if conditions:
            return query.filter(or_(*conditions))
        return query
    
    def _apply_dict_where(self, query, where_dict):
        """应用字典形式的where条件"""
        # 这里可以实现更复杂的查询逻辑
        # 暂时简化处理
        return query
    
    def _apply_order_by(self, query, order_by):
        """应用排序"""
        for order_clause in order_by:
            if " " in order_clause:
                field, direction = order_clause.split(" ", 1)
                direction = direction.lower()
                
                if hasattr(self.model, field):
                    attr = getattr(self.model, field)
                    if direction == "desc":
                        query = query.order_by(desc(attr))
                    else:
                        query = query.order_by(asc(attr))
        return query


# 用户管理视图
class UserAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__()
        self.identity = "user"
        self.name = "用户管理"
        self.label = "用户管理"
        self.icon = "fa fa-users"
        self.model = UserProfile
        
        # 搜索字段
        self.searchable_fields = ["name", "nick_name", "mobile"]
        
        # 排序字段
        self.sortable_fields = ["name", "mobile", "created_at"]
        
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
        super().__init__()
        self.identity = "activity_type"
        self.name = "活动类型"
        self.label = "活动类型"
        self.icon = "fa fa-tags"
        self.model = ActivityType
        
        self.searchable_fields = ["name", "introduction"]
        self.sortable_fields = ["name", "index_num", "created_at"]
        self.fields_default_sort = [("index_num", False)]  # 按排序号升序
        self.page_size = 25


# 活动管理视图
class ActivityAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__()
        self.identity = "activity"
        self.name = "活动管理"
        self.label = "活动管理"
        self.icon = "fa fa-calendar"
        self.model = Activity
        
        self.searchable_fields = ["title", "content", "address"]
        self.sortable_fields = ["title", "start_date", "created_at", "audit"]
        self.fields_default_sort = [("created_at", True)]  # 按创建时间倒序
        self.page_size = 25


# 分享设置管理视图
class SharingSetAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__()
        self.identity = "sharing_set"
        self.name = "分享设置"
        self.label = "分享设置"
        self.icon = "fa fa-share-alt"
        self.model = SharingSet
        
        self.searchable_fields = ["title"]
        self.sortable_fields = ["title", "page_type", "created_at"]
        self.page_size = 25


# 用户收藏管理视图
class UserCollectionAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__()
        self.identity = "user_collection"
        self.name = "用户收藏"
        self.label = "用户收藏"
        self.icon = "fa fa-star"
        self.model = CollectionUser
        
        self.sortable_fields = ["created_at"]
        self.fields_default_sort = [("created_at", True)]
        self.page_size = 25


# 举报管理视图
class UserReportAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__()
        self.identity = "user_report"
        self.name = "举报管理"
        self.label = "举报管理"
        self.icon = "fa fa-exclamation-triangle"
        self.model = ReportUser
        
        self.searchable_fields = ["reason"]
        self.sortable_fields = ["created_at"]
        self.fields_default_sort = [("created_at", True)]
        self.page_size = 25


# 评论管理视图
class CommentAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__()
        self.identity = "comment"
        self.name = "评论管理"
        self.label = "评论管理"
        self.icon = "fa fa-comments"
        self.model = Comment
        
        self.searchable_fields = ["content"]
        self.sortable_fields = ["created_at"]
        self.fields_default_sort = [("created_at", True)]
        self.page_size = 25


# 反馈管理视图
class FeedbackAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__()
        self.identity = "feedback"
        self.name = "反馈管理"
        self.label = "反馈管理"
        self.icon = "fa fa-envelope"
        self.model = Feedback
        
        self.searchable_fields = ["title", "content"]
        self.sortable_fields = ["created_at", "is_handled"]
        self.fields_default_sort = [("created_at", True)]
        self.page_size = 25


# 活动报名管理视图
class ActivityUserInfoAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__()
        self.identity = "activity_user_info"
        self.name = "活动报名"
        self.label = "活动报名"
        self.icon = "fa fa-users"
        self.model = ActivityUserInfo
        
        self.searchable_fields = ["username", "wechat"]
        self.sortable_fields = ["created_at", "user_type"]
        self.fields_default_sort = [("created_at", True)]
        self.page_size = 25


# 系统用户管理视图
class SysUserAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__()
        self.identity = "sys_user"
        self.name = "系统用户"
        self.label = "系统用户"
        self.icon = "fa fa-cog"
        self.model = SysUser
        
        self.searchable_fields = ["name", "introduction"]
        self.sortable_fields = ["name", "created_at"]
        self.page_size = 25


# 系统消息管理视图
class SystemMessageAdmin(SQLAlchemyModelView):
    def __init__(self):
        super().__init__()
        self.identity = "sys_message"
        self.name = "系统消息"
        self.label = "系统消息"
        self.icon = "fa fa-bell"
        self.model = SysMessage
        
        self.searchable_fields = ["title", "content"]
        self.sortable_fields = ["created_at", "status"]
        self.fields_default_sort = [("created_at", True)]
        self.page_size = 25


# 创建Admin实例
admin = BaseAdmin(
    title="一起呦管理系统",
    base_url="/YiqiAdmin0001shujian",
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