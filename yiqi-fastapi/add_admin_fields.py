#!/usr/bin/env python3
"""
为用户表添加管理员相关字段的脚本
"""
from sqlalchemy import text
from app.database import engine

def add_admin_fields():
    """添加管理员相关字段"""
    
    # 添加字段的SQL语句
    sql_statements = [
        "ALTER TABLE users_userprofile ADD COLUMN hashed_password VARCHAR(128) NULL COMMENT '密码hash'",
        "ALTER TABLE users_userprofile ADD COLUMN is_admin BOOLEAN DEFAULT FALSE COMMENT '是否管理员'"
    ]
    
    with engine.connect() as conn:
        for sql in sql_statements:
            try:
                conn.execute(text(sql))
                conn.commit()
                print(f"执行成功: {sql}")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print(f"字段已存在，跳过: {sql}")
                else:
                    print(f"执行失败: {sql}, 错误: {e}")
                    raise

if __name__ == "__main__":
    add_admin_fields()
    print("数据库字段添加完成!")