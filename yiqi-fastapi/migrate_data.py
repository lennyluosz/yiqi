#!/usr/bin/env python3
"""
数据迁移脚本：从Django表结构迁移到FastAPI表结构
"""

import pymysql
from datetime import datetime
import uuid

# 数据库连接配置
DB_CONFIG = {
    'host': '192.168.14.200',
    'user': 'yiqi',
    'password': 'admin123456',
    'database': 'tytt',
    'charset': 'utf8mb4'
}

# Django表名到FastAPI表名的映射
TABLE_MAPPING = {
    # 用户表
    'users_userprofile': 'users_userprofile',
    
    # 活动相关表
    'activity_activitytypemodel': 'activity_activitytype',
    'activity_activitymodel': 'activity_activity',
    'activity_activityimagesmodel': 'activity_activityimage',
    'activity_slidemodels': 'activity_slide',
    
    # 用户操作表
    'userOperation_activityuserinfo': 'useroperation_activityuserinfo',
    'userOperation_sharingusermodel': 'useroperation_sharinguser',
    'userOperation_collectionusermodel': 'useroperation_collectionuser',
    'userOperation_reporttionusermodel': 'useroperation_reportuser',
    'userOperation_browseusermodel': 'useroperation_browseuser',
    'userOperation_commentsmodels': 'useroperation_comment',
    'userOperation_feedbackmodels': 'useroperation_feedback',
    
    # 消息系统表
    'messagess_sysusermodel': 'messages_sysuser',
    'messagess_sysuserthemenumodel': 'messages_sysusermenu',
    'userOperation_sysmessages': 'messages_sysmessage',
    
    # 分享设置表
    'SharingSet_sharingsetmodel': 'sharing_sharingset'
}

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def check_old_tables_exist(conn):
    """检查原始Django表是否存在"""
    cursor = conn.cursor()
    existing_tables = []
    
    for old_table in TABLE_MAPPING.keys():
        cursor.execute("SHOW TABLES LIKE %s", (old_table,))
        if cursor.fetchone():
            existing_tables.append(old_table)
    
    cursor.close()
    return existing_tables

def migrate_sharing_data(conn):
    """迁移分享数据"""
    cursor = conn.cursor()
    
    # 检查原表是否存在
    cursor.execute("SHOW TABLES LIKE 'SharingSet_sharingsetmodel'")
    if not cursor.fetchone():
        print("原分享表不存在，跳过分享数据迁移")
        cursor.close()
        return
    
    # 查询原数据
    cursor.execute("""
        SELECT id, set_path, title, imageUrl, addtime 
        FROM SharingSet_sharingsetmodel
    """)
    
    old_data = cursor.fetchall()
    print(f"找到 {len(old_data)} 条分享数据")
    
    if old_data:
        # 清空目标表
        cursor.execute("DELETE FROM sharing_sharingset")
        
        # 插入新数据
        insert_sql = """
            INSERT INTO sharing_sharingset 
            (id, page_type, title, image_url, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        for row in old_data:
            id_val, set_path, title, image_url, add_time = row
            now = datetime.now()
            
            cursor.execute(insert_sql, (
                id_val, set_path, title, image_url, add_time, now
            ))
        
        conn.commit()
        print(f"成功迁移 {len(old_data)} 条分享数据")
    
    cursor.close()

def migrate_activity_types(conn):
    """迁移活动类型数据"""
    cursor = conn.cursor()
    
    # 检查原表是否存在
    cursor.execute("SHOW TABLES LIKE 'activity_activitytypemodel'")
    if not cursor.fetchone():
        print("原活动类型表不存在，创建默认数据")
        # 创建一些默认的活动类型
        default_types = [
            (1, '户外运动', '各种户外运动活动', 0),
            (2, '聚会社交', '朋友聚会、社交活动', 1),
            (3, '学习分享', '学习交流、知识分享', 2),
            (4, '旅行探险', '旅行、探险活动', 3),
            (5, '其他活动', '其他类型活动', 4)
        ]
        
        cursor.execute("DELETE FROM activity_activitytype")
        
        insert_sql = """
            INSERT INTO activity_activitytype 
            (id, name, introduction, index_num, created_at) 
            VALUES (%s, %s, %s, %s, %s)
        """
        
        for type_id, name, intro, index_num in default_types:
            cursor.execute(insert_sql, (
                type_id, name, intro, index_num, datetime.now()
            ))
        
        conn.commit()
        print("创建了默认活动类型数据")
        cursor.close()
        return
    
    # 迁移原有数据
    cursor.execute("""
        SELECT id, name, cover_image, Introduction, indexnum, addtime 
        FROM activity_activitytypemodel
    """)
    
    old_data = cursor.fetchall()
    print(f"找到 {len(old_data)} 条活动类型数据")
    
    if old_data:
        cursor.execute("DELETE FROM activity_activitytype")
        
        insert_sql = """
            INSERT INTO activity_activitytype 
            (id, name, cover_image, introduction, index_num, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        for row in old_data:
            id_val, name, cover_image, introduction, index_num, add_time = row
            cursor.execute(insert_sql, (
                id_val, name, cover_image, introduction, index_num, add_time
            ))
        
        conn.commit()
        print(f"成功迁移 {len(old_data)} 条活动类型数据")
    
    cursor.close()

def migrate_users(conn):
    """迁移用户数据"""
    cursor = conn.cursor()
    
    # 检查原表是否存在
    cursor.execute("SHOW TABLES LIKE 'users_userprofile'")
    if not cursor.fetchone():
        print("用户表不存在，创建测试用户")
        # 创建一个测试用户
        test_user_data = {
            'id': 1,
            'openid': 'test_openid_123',
            'avatar_url': '',
            'country': '中国',
            'user_bh': uuid.uuid4().hex,
            'province': '广东省',
            'city': '深圳市',
            'language': 'zh_CN',
            'background': '',
            'nick_name': '测试用户',
            'name': '测试用户',
            'birthday': datetime.now().date(),
            'avatar': '',
            'mobile': '',
            'gender': '1',
            'signature': '世界为你转身，因为你肯冒险！',
            'agreement': True,
            'email': '',
            'is_active': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        insert_sql = """
            INSERT INTO users_userprofile 
            (id, openid, avatar_url, country, user_bh, province, city, language,
             background, nick_name, name, birthday, avatar, mobile, gender,
             signature, agreement, email, is_active, created_at, updated_at) 
            VALUES (%(id)s, %(openid)s, %(avatar_url)s, %(country)s, %(user_bh)s,
                   %(province)s, %(city)s, %(language)s, %(background)s, %(nick_name)s,
                   %(name)s, %(birthday)s, %(avatar)s, %(mobile)s, %(gender)s,
                   %(signature)s, %(agreement)s, %(email)s, %(is_active)s,
                   %(created_at)s, %(updated_at)s)
        """
        
        cursor.execute(insert_sql, test_user_data)
        conn.commit()
        print("创建了测试用户")
    else:
        print("用户表已存在，保持现有数据")
    
    cursor.close()

def migrate_system_users(conn):
    """迁移系统用户数据"""
    cursor = conn.cursor()
    
    # 创建默认系统用户
    system_user_data = {
        'id': 1,
        'name': '系统通知',
        'introduction': '系统消息推送服务',
        'user_type': '0',
        'avatar': '',
        'created_at': datetime.now()
    }
    
    cursor.execute("DELETE FROM messages_sysuser WHERE id = 1")
    
    insert_sql = """
        INSERT INTO messages_sysuser 
        (id, name, introduction, user_type, avatar, created_at) 
        VALUES (%(id)s, %(name)s, %(introduction)s, %(user_type)s, %(avatar)s, %(created_at)s)
    """
    
    cursor.execute(insert_sql, system_user_data)
    conn.commit()
    print("创建了默认系统用户")
    
    cursor.close()

def main():
    """主函数"""
    print("开始数据迁移...")
    
    try:
        conn = get_db_connection()
        print("数据库连接成功")
        
        # 检查原表
        existing_tables = check_old_tables_exist(conn)
        print(f"找到 {len(existing_tables)} 个原始表")
        
        # 执行迁移
        migrate_sharing_data(conn)
        migrate_activity_types(conn)
        migrate_users(conn)
        migrate_system_users(conn)
        
        print("数据迁移完成！")
        
    except Exception as e:
        print(f"迁移失败: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()