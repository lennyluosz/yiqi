#!/usr/bin/env python3
"""
导入用户数据，处理Django到FastAPI的字段映射
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

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def import_user_data():
    """导入用户数据"""
    # 原始用户数据（从SQL中提取的两个用户）
    original_users = [
        {
            'id': 1,
            'password': 'pbkdf2_sha256$36000$84Asj8ez6gvY$zv2wBScM6CfmynQdbW18hgBujBti3HYlM8kyQbbcj4U=',
            'last_login': '2018-07-10 21:17:28.683952',
            'is_superuser': 1,
            'username': 'shujian',
            'first_name': '',
            'last_name': '',
            'email': '',
            'is_staff': 1,
            'is_active': 1,
            'date_joined': '2018-06-30 21:55:12.637351',
            'openid': '',
            'avatarUrl': '',
            'country': '',
            'user_bh': 'e61002de2f5c4cf5a1f21b324b564941',
            'province': '',
            'city': '',
            'language': '',
            'background': '/default/default.jpg',
            'nickName': '',
            'name': '',
            'birthay': '2018-06-30',
            'avatar': '',
            'mobile': None,
            'gender': '1',
            'thesignature': '',
            'agreement': 0,
            'email_user': '',
            'add_time': '2018-06-30 21:55:12.637421'
        },
        {
            'id': 12,
            'password': 'pbkdf2_sha256$36000$UIPPaG1r0yaG$7ztu5NXbkM1Yo+jdDOhxZpKuSWhvAYoQzi6wSydsn+I=',
            'last_login': None,
            'is_superuser': 0,
            'username': 'orTEV0YkH3oI5ZunYB85ZfgQQut4',
            'first_name': '',
            'last_name': '',
            'email': '',
            'is_staff': 0,
            'is_active': 1,
            'date_joined': '2018-07-10 21:57:17.753989',
            'openid': 'orTEV0YkH3oI5ZunYB85ZfgQQut4',
            'avatarUrl': 'https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTLQaWXfpntwPpg2Khv8J437OJ8lI3WdTElajibufpTJfjeMBibyES6TpxELqFS8P5Hf0v03WHgia45BQ/132',
            'country': 'China',
            'user_bh': '935a1576b257457fabe25a917392b4c0',
            'province': 'Beijing',
            'city': 'Chaoyang',
            'language': 'zh_CN',
            'background': '/default/default.jpg',
            'nickName': '啊哈哈',
            'name': '啊哈哈',
            'birthay': '2018-07-10',
            'avatar': 'UserProFilebg/avatar/orTEV0YkH3oI5ZunYB85ZfgQQut4.png',
            'mobile': None,
            'gender': '1',
            'thesignature': '世界为你转身，因为你肯冒险！',
            'agreement': 0,
            'email_user': None,
            'add_time': '2018-07-10 21:57:17.754027'
        }
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 清空现有用户数据
        cursor.execute("DELETE FROM users_userprofile")
        
        # 插入新数据（映射到FastAPI表结构）
        insert_sql = """
            INSERT INTO users_userprofile 
            (id, openid, avatar_url, country, user_bh, province, city, language,
             background, nick_name, name, birthday, avatar, mobile, gender,
             signature, agreement, email, is_active, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        imported_count = 0
        
        for user_data in original_users:
            try:
                # 字段映射和数据处理
                mapped_data = {
                    'id': user_data['id'],
                    'openid': user_data['openid'] or '',
                    'avatar_url': user_data['avatarUrl'] or '',
                    'country': user_data['country'] or '',
                    'user_bh': user_data['user_bh'] or uuid.uuid4().hex,
                    'province': user_data['province'] or '',
                    'city': user_data['city'] or '',
                    'language': user_data['language'] or '',
                    'background': user_data['background'] or '',
                    'nick_name': user_data['nickName'] or user_data['username'],
                    'name': user_data['name'] or user_data['username'],
                    'birthday': datetime.strptime(user_data['birthay'], '%Y-%m-%d').date() if user_data['birthay'] else datetime.now().date(),
                    'avatar': user_data['avatar'] or '',
                    'mobile': user_data['mobile'] or '',
                    'gender': user_data['gender'] or '1',
                    'signature': user_data['thesignature'] or '世界为你转身，因为你肯冒险！',
                    'agreement': bool(user_data['agreement']),
                    'email': user_data.get('email_user') or '',
                    'is_active': bool(user_data['is_active']),
                    'created_at': datetime.strptime(user_data['add_time'], '%Y-%m-%d %H:%M:%S.%f'),
                    'updated_at': datetime.now()
                }
                
                cursor.execute(insert_sql, (
                    mapped_data['id'],
                    mapped_data['openid'],
                    mapped_data['avatar_url'],
                    mapped_data['country'],
                    mapped_data['user_bh'],
                    mapped_data['province'],
                    mapped_data['city'],
                    mapped_data['language'],
                    mapped_data['background'],
                    mapped_data['nick_name'],
                    mapped_data['name'],
                    mapped_data['birthday'],
                    mapped_data['avatar'],
                    mapped_data['mobile'],
                    mapped_data['gender'],
                    mapped_data['signature'],
                    mapped_data['agreement'],
                    mapped_data['email'],
                    mapped_data['is_active'],
                    mapped_data['created_at'],
                    mapped_data['updated_at']
                ))
                
                imported_count += 1
                print(f"✅ 导入用户: {mapped_data['name']} (ID: {mapped_data['id']})")
                
            except Exception as e:
                print(f"❌ 导入用户 {user_data.get('username', 'unknown')} 失败: {e}")
                continue
        
        conn.commit()
        print(f"\n🎉 成功导入 {imported_count} 个用户")
        
        # 验证数据
        cursor.execute("SELECT id, name, nick_name, openid, city FROM users_userprofile ORDER BY id")
        results = cursor.fetchall()
        
        print("\n📋 导入的用户列表:")
        for row in results:
            openid_display = row[3][:20] + "..." if len(row[3]) > 20 else row[3]
            print(f"- ID {row[0]}: {row[1]} ({row[2]}) - {row[4]} - {openid_display}")
            
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🚀 开始导入用户数据...")
    import_user_data()