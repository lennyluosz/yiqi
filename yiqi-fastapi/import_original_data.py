#!/usr/bin/env python3
"""
直接从原始SQL文件导入数据
"""

import pymysql
import re
import os
from datetime import datetime

# 数据库连接配置
DB_CONFIG = {
    'host': '192.168.14.200',
    'user': 'yiqi',
    'password': 'admin123456',
    'database': 'tytt',
    'charset': 'utf8mb4'
}

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def extract_insert_statements(sql_file_path):
    """从SQL文件中提取INSERT语句"""
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到所有INSERT语句
    insert_pattern = r'INSERT INTO\s+`([^`]+)`\s+VALUES\s+\((.*?)\);'
    matches = re.findall(insert_pattern, content, re.DOTALL | re.IGNORECASE)
    
    insert_data = {}
    for table_name, values_str in matches:
        if table_name not in insert_data:
            insert_data[table_name] = []
        
        # 解析VALUES部分 - 这里简化处理，直接保存原始VALUES
        insert_data[table_name].append(values_str)
    
    return insert_data

def migrate_sharing_data(conn):
    """迁移分享数据"""
    print("开始迁移分享数据...")
    cursor = conn.cursor()
    
    # 直接执行原始SQL中的分享数据
    sharing_inserts = [
        (1, '0', '旅行真正的快乐不在于目的地，而在于它的过程。', 'SharingSet/18/04/ce7a3e1c8cce43d0801f2df98c386aec/tooopen_sy_141357577876.jpg', '2018-07-04 10:29:58.000000'),
        (2, '0', '人生就是一场旅行，不在乎目的地，在乎的应该是沿途的风景以及看风景的心情。', 'SharingSet/18/04/ce7a3e1c8cce43d0801f2df98c386aec/tooopen_sy_115615561524369.jpg', '2018-07-04 10:36:14.000000'),
        (3, '1', '梦想，并不奢侈，只要勇敢地迈出第一步。', 'SharingSet/18/04/fb5be8762d3e478abd6b0fd5edf93a14/tooopen_sy_234110021676.jpg', '2018-07-04 11:05:33.000000'),
        (4, '1', '要么读书、要么旅行，灵魂和身体，必须有一个在路上。', 'SharingSet/18/04/fb5be8762d3e478abd6b0fd5edf93a14/timg.jpeg', '2018-07-04 11:06:23.000000'),
        (5, '1', '人生最好的旅行，就是你在一个陌生的地方，发现一种久违的感动。', 'SharingSet/18/04/3f1dc3c49a424e3ba05a26fb25753a80/tooopen_sy_212262971441.jpg', '2018-07-04 11:54:41.000000'),
        (6, '1', '因为有梦，所以勇敢出发，选择出发，便只顾风雨兼程。', 'SharingSet/18/04/3f1dc3c49a424e3ba05a26fb25753a80/tooopen_sy_191622676468.jpg', '2018-07-04 11:56:06.000000'),
        (7, '1', '每个人心中，都会有一个古镇情怀，流水江南，烟笼人家。', 'SharingSet/18/04/3f1dc3c49a424e3ba05a26fb25753a80/tooopen_sy_123995289533.jpg', '2018-07-04 11:56:53.000000'),
        (8, '0', '记录沿途的心情，那样的生活才是我想要的。', 'SharingSet/18/04/672430092210403c8b56c262bcb9215e/tooopen_sy_141343367572.jpg', '2018-07-04 13:46:16.000000'),
        (9, '0', '和TA一起，在路上遇见最真实的自己。', 'SharingSet/18/04/672430092210403c8b56c262bcb9215e/tooopen_sy_233746431863.jpg', '2018-07-04 13:47:37.000000'),
        (10, '0', '要学会随遇而安，淡然一点，走走停停。', 'SharingSet/18/04/672430092210403c8b56c262bcb9215e/tooopen_sy_120548398993.jpg', '2018-07-04 13:50:46.000000')
    ]
    
    # 清空现有数据
    cursor.execute("DELETE FROM sharing_sharingset")
    
    # 插入数据到新表结构
    insert_sql = """
        INSERT INTO sharing_sharingset 
        (id, page_type, title, image_url, created_at, updated_at) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    for row in sharing_inserts:
        id_val, page_type, title, image_url, created_at = row
        # 将datetime字符串转换为datetime对象
        created_dt = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S.%f')
        
        cursor.execute(insert_sql, (
            id_val, page_type, title, image_url, created_dt, created_dt
        ))
    
    conn.commit()
    print(f"成功迁移 {len(sharing_inserts)} 条分享数据")
    cursor.close()

def import_sql_directly(conn, sql_file_path):
    """尝试直接导入部分原始SQL"""
    print("尝试直接导入原始SQL数据...")
    cursor = conn.cursor()
    
    try:
        # 读取SQL文件
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 提取活动类型数据
        activity_type_pattern = r'INSERT INTO `activity_activitytypemodel` VALUES \((.*?)\);'
        activity_type_matches = re.findall(activity_type_pattern, sql_content, re.DOTALL)
        
        if activity_type_matches:
            print(f"找到 {len(activity_type_matches)} 条活动类型数据")
            
            # 清空现有数据
            cursor.execute("DELETE FROM activity_activitytype")
            
            for match in activity_type_matches:
                # 解析每行数据 - 这里需要仔细处理
                # 示例: 1, '户外运动', 'cover.jpg', '运动类活动', 0, '2018-07-04 10:29:58.000000'
                try:
                    # 简单解析（实际项目中可能需要更复杂的解析）
                    values = [v.strip().strip("'\"") for v in match.split(',')]
                    if len(values) >= 5:
                        cursor.execute("""
                            INSERT INTO activity_activitytype 
                            (id, name, cover_image, introduction, index_num, created_at) 
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            int(values[0]),
                            values[1],
                            values[2] if values[2] != 'NULL' else None,
                            values[3],
                            int(values[4]),
                            datetime.now()
                        ))
                except Exception as e:
                    print(f"解析活动类型数据失败: {e}")
                    continue
            
            conn.commit()
            print("活动类型数据导入完成")
        
        # 可以继续添加其他表的数据导入...
        
    except Exception as e:
        print(f"直接导入SQL失败: {e}")
        conn.rollback()
    finally:
        cursor.close()

def create_sample_data(conn):
    """创建一些示例数据用于测试"""
    print("创建示例数据...")
    cursor = conn.cursor()
    
    try:
        # 创建示例活动类型
        cursor.execute("DELETE FROM activity_activitytype")
        activity_types = [
            (1, '户外运动', None, '各种户外运动活动', 0),
            (2, '聚会社交', None, '朋友聚会、社交活动', 1),
            (3, '学习分享', None, '学习交流、知识分享', 2),
            (4, '旅行探险', None, '旅行、探险活动', 3),
            (5, '其他活动', None, '其他类型活动', 4)
        ]
        
        for type_data in activity_types:
            cursor.execute("""
                INSERT INTO activity_activitytype 
                (id, name, cover_image, introduction, index_num, created_at) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (*type_data, datetime.now()))
        
        # 创建系统用户
        cursor.execute("DELETE FROM messages_sysuser WHERE id = 1")
        cursor.execute("""
            INSERT INTO messages_sysuser 
            (id, name, introduction, user_type, avatar, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (1, '系统通知', '系统消息推送服务', '0', '', datetime.now()))
        
        conn.commit()
        print("示例数据创建完成")
        
    except Exception as e:
        print(f"创建示例数据失败: {e}")
        conn.rollback()
    finally:
        cursor.close()

def main():
    """主函数"""
    print("开始数据导入...")
    
    sql_file_path = '/dataShared/tempDev/git/yiqi/backend/sql/yiqi.sql'
    
    try:
        conn = get_db_connection()
        print("数据库连接成功")
        
        # 迁移分享数据
        migrate_sharing_data(conn)
        
        # 创建示例数据
        create_sample_data(conn)
        
        # 尝试导入原始SQL中的其他数据
        if os.path.exists(sql_file_path):
            import_sql_directly(conn, sql_file_path)
        else:
            print(f"SQL文件不存在: {sql_file_path}")
        
        print("数据导入完成！")
        
        # 验证数据
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sharing_sharingset")
        sharing_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM activity_activitytype")
        type_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM messages_sysuser")
        sysuser_count = cursor.fetchone()[0]
        
        print(f"\n数据验证:")
        print(f"- 分享数据: {sharing_count} 条")
        print(f"- 活动类型: {type_count} 条")
        print(f"- 系统用户: {sysuser_count} 条")
        
        cursor.close()
        
    except Exception as e:
        print(f"导入失败: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()