#!/usr/bin/env python3
"""
清理构建文件
"""

import os
import shutil
import glob

def clean_build_files():
    """清理构建相关的文件和目录"""
    directories_to_remove = [
        "build",
        "dist",
    ]
    
    # 添加 .egg-info 目录
    egg_info_dirs = glob.glob("*.egg-info")
    directories_to_remove.extend(egg_info_dirs)
    
    # 删除目录
    for dir_name in directories_to_remove:
        if os.path.exists(dir_name):
            print(f"🧹 删除: {dir_name}")
            shutil.rmtree(dir_name)
        else:
            print(f"ℹ️  目录不存在: {dir_name}")
    
    # 清理 __pycache__
    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            print(f"🧹 清理: {pycache_path}")
            shutil.rmtree(pycache_path)
    
    print("✅ 清理完成!")

if __name__ == "__main__":
    clean_build_files()
