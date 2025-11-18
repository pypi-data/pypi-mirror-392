#!/usr/bin/env python3
"""
PyPI 发布脚本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, check=True):
    """运行命令并检查结果"""
    print(f"🚀 执行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ 命令失败: {cmd}")
        print(f"错误输出: {result.stderr}")
        return False
    return True

def clean_previous_builds():
    """清理之前的构建文件"""
    print("🧹 清理构建文件...")
    
    directories_to_remove = ["build", "dist"]
    
    for dir_name in directories_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ 删除: {dir_name}")
    
    # 清理 .egg-info 目录
    import glob
    for egg_info in glob.glob("*.egg-info"):
        if os.path.exists(egg_info):
            shutil.rmtree(egg_info)
            print(f"✅ 删除: {egg_info}")

def check_version():
    """检查版本号"""
    try:
        init_file = Path("src/circuit_denoiser/__init__.py")
        with open(init_file, 'r') as f:
            content = f.read()
            if '__version__' in content:
                import re
                version_match = re.search(r"__version__ = ['\"]([^'\"]*)['\"]", content)
                if version_match:
                    version = version_match.group(1)
                    print(f"📦 当前版本: {version}")
                    return version
    except Exception as e:
        print(f"❌ 检查版本失败: {e}")
    
    return "1.0.1"

def build_package():
    """构建包"""
    print("🔨 构建分发包...")
    if not run_command("python -m build"):
        print("尝试使用备用构建方法...")
        if run_command("python setup.py sdist bdist_wheel"):
            print("✅ 备用构建成功")
        else:
            print("❌ 所有构建方法都失败")
            return False
    return True

def test_install():
    """测试安装"""
    print("🧪 测试安装...")
    whl_files = list(Path("dist").glob("*.whl"))
    if whl_files:
        return run_command(f"pip install --force-reinstall {whl_files[0]}")
    return False

def upload_to_pypi(test=False):
    """上传到 PyPI"""
    repository = "--repository testpypi" if test else ""
    print(f"📤 上传到 {'TestPyPI' if test else 'PyPI'}...")
    
    # 检查是否有上传凭据
    if not test:
        confirm = input("⚠️  确认上传到正式 PyPI? (输入 'yes' 继续): ").strip()
        if confirm.lower() != "yes":
            print("❌ 上传取消")
            return False
    
    return run_command(f"twine upload {repository} dist/*")

def main():
    """主发布流程"""
    print("=" * 60)
    print("PyPI 发布流程 - AI Circuit Denoiser")
    print("=" * 60)
    
    # 检查版本
    version = check_version()
    
    # 清理
    clean_previous_builds()
    
    # 构建
    if not build_package():
        return
    
    # 检查生成的文件
    dist_files = list(Path("dist").glob("*"))
    if not dist_files:
        print("❌ 没有生成分发文件")
        return
    
    print("✅ 生成的分发文件:")
    for file in dist_files:
        print(f"   - {file.name} ({file.stat().st_size / 1024:.1f} KB)")
    
    # 询问是否测试安装
    test_install_answer = input("🧪 是否测试安装? (y/n): ").lower().strip()
    if test_install_answer == 'y':
        if not test_install():
            print("❌ 测试安装失败")
            return
        print("✅ 测试安装成功")
        
        # 测试基本功能
        print("🧪 测试基本功能...")
        run_command("ai-circuit-denoise --help", check=False)
        run_command("ai-circuit-denoise-gui --help", check=False)
    
    # 询问上传目标
    print("\n选择上传目标:")
    print("1. TestPyPI (测试环境)")
    print("2. PyPI (正式环境)")
    choice = input("请输入选择 (1/2): ").strip()
    
    if choice == "1":
        if upload_to_pypi(test=True):
            print("✅ 已上传到 TestPyPI")
            print("💡 测试安装命令:")
            print("   pip install --index-url https://test.pypi.org/simple/ ai-circuit-denoise")
        else:
            print("❌ 上传到 TestPyPI 失败")
    elif choice == "2":
        if upload_to_pypi(test=False):
            print("✅ 已上传到 PyPI")
            print("🎉 发布完成!")
            print("💡 用户现在可以通过以下命令安装:")
            print("   pip install ai-circuit-denoise")
            print("   ai-circuit-denoise-gui --desktop")
        else:
            print("❌ 上传到 PyPI 失败")
    else:
        print("❌ 无效选择")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
