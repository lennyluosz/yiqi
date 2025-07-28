#!/usr/bin/env python3
"""
导入活动类型数据
"""

import pymysql
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

def import_activity_types():
    """导入活动类型数据"""
    # 原始数据
    activity_types = [
        (1, '城市探险', 'ActivityTypeModel/18/01/1a3398f04eab4bcf86b779d26f1f8991/tooopen_sy_183358335862037.jpg', '对城市中的人造建筑展开的探险...', 0, '2018-07-01 02:05:17.000000'),
        (2, '骑行', 'ActivityTypeModel/18/01/1a3398f04eab4bcf86b779d26f1f8991/tooopen_sy_119046289467.jpg', '骑行是一种健康自然的运动旅游方式 ，能充分享受旅行过程之美 。一辆单车，一个背包即可出行 ，简单又环保。在不断而来的困难当中体验挑战，在旅途的终点体验成功', 1, '2018-07-01 02:07:02.000000'),
        (3, '读书', 'ActivityTypeModel/18/01/1a3398f04eab4bcf86b779d26f1f8991/tooopen_sy_234299941827.jpg', '阅读是一种习惯，书中自有颜如玉！', 2, '2018-07-01 02:08:07.000000'),
        (4, '游戏', 'ActivityTypeModel/18/01/1a3398f04eab4bcf86b779d26f1f8991/tooopen_sy_126646593189.jpg', '玩玩游戏，时刻放松一下！', 3, '2018-07-01 02:09:10.000000'),
        (5, '旅行', 'ActivityTypeModel/18/01/1a3398f04eab4bcf86b779d26f1f8991/tooopen_sy_230185184143.jpg', '看看身边的景色和事物，行万里路，读万卷书！', 4, '2018-07-01 02:10:20.000000'),
        (6, '其他', 'ActivityTypeModel/18/01/1a3398f04eab4bcf86b779d26f1f8991/tooopen_sy_211426474221.jpg', '其余，不分人与物！', 5, '2018-07-01 02:13:00.000000')
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 清空现有数据
        cursor.execute("DELETE FROM activity_activitytype")
        
        # 插入新数据
        insert_sql = """
            INSERT INTO activity_activitytype 
            (id, name, cover_image, introduction, index_num, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        for type_data in activity_types:
            id_val, name, cover_image, introduction, index_num, created_at_str = type_data
            
            # 转换时间格式
            created_at = datetime.strptime(created_at_str, '%Y-%m-%d %H:%M:%S.%f')
            
            cursor.execute(insert_sql, (
                id_val, name, cover_image, introduction, index_num, created_at
            ))
        
        conn.commit()
        print(f"成功导入 {len(activity_types)} 条活动类型数据")
        
        # 验证数据
        cursor.execute("SELECT id, name, introduction FROM activity_activitytype ORDER BY index_num")
        results = cursor.fetchall()
        
        print("\n导入的活动类型:")
        for row in results:
            print(f"- {row[0]}: {row[1]} - {row[2][:50]}...")
            
    except Exception as e:
        print(f"导入失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    import_activity_types()