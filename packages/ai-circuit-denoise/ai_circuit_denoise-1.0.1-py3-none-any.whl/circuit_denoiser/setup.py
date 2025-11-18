#!/usr/bin/env python3
"""
Setup script for AI Circuit Denoiser
兼容性脚本，主要配置在 pyproject.toml 中
"""

from setuptools import setup, find_packages
import os
import sys
import platform
from pathlib import Path

def get_version():
    """从 __init__.py 获取版本号"""
    try:
        version_file = Path(__file__).parent / "circuit_denoiser" / "__init__.py"
        with open(version_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"\'')
    except:
        pass
    return "1.0.1"

def get_long_description():
    """获取长描述"""
    try:
        readme_path = Path(__file__).parent / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                return f.read()
    except:
        pass
    return "AI-based circuit image denoising tool for electronics engineers"

def create_desktop_shortcut():
    """安装后创建桌面快捷方式"""
    if 'install' in sys.argv:
        try:
            # 延迟导入
            sys.path.insert(0, str(Path(__file__).parent))
            from circuit_denoiser.create_shortcut import create_desktop_shortcut as create_shortcut
            create_shortcut()
        except Exception as e:
            print(f"注意: 无法创建桌面快捷方式: {e}")

# 基础配置
setup(
    name="ai-circuit-denoise",
    version=get_version(),
    packages=find_packages(),
    package_dir={'circuit_denoiser': '.'},
    include_package_data=True,
)

# 安装后操作
if __name__ == "__main__":
    create_desktop_shortcut()
    
    # 显示安装成功信息
    print("\n" + "="*60)
    print("🎉 AI Circuit Denoiser 安装成功!")
    print("="*60)
