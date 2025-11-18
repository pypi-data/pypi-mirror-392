#!/usr/bin/env python3
"""
桌面快捷方式创建脚本
"""

import os
import sys
import platform
from pathlib import Path

def create_desktop_shortcut():
    """为当前平台创建桌面快捷方式"""
    system = platform.system()
    
    print(f"为 {system} 创建桌面快捷方式...")
    
    if system == "Darwin":  # macOS
        create_macos_app()
    elif system == "Windows":
        create_windows_shortcut()
    elif system == "Linux":
        create_linux_desktop()
    else:
        print(f"不支持的系统: {system}")

def create_macos_app():
    """创建macOS应用包"""
    try:
        project_dir = Path(__file__).parent
        app_name = "AI Circuit Denoiser.app"
        app_path = project_dir / app_name
        
        # 创建应用目录结构
        contents_dir = app_path / "Contents" / "MacOS"
        contents_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建Info.plist
        info_plist = app_path / "Contents" / "Info.plist"
        info_plist_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launch</string>
    <key>CFBundleName</key>
    <string>AI Circuit Denoiser</string>
    <key>CFBundleIdentifier</key>
    <string>com.circuitai.denoiser</string>
    <key>CFBundleVersion</key>
    <string>1.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>'''
        
        with open(info_plist, 'w') as f:
            f.write(info_plist_content)
        
        # 创建启动脚本
        launch_script = contents_dir / "launch"
        launch_script_content = f'''#!/bin/bash
# 切换到项目目录
cd "{project_dir}"

# 激活conda环境（如果存在）
if [ -n "$CONDA_PREFIX" ]; then
    source "$CONDA_PREFIX/etc/profile.d/conda.sh"
    conda activate circuit_ai 2>/dev/null || true
fi

# 启动应用
python -m circuit_denoiser.main --desktop
'''
        
        with open(launch_script, 'w') as f:
            f.write(launch_script_content)
        
        # 设置执行权限
        launch_script.chmod(0o755)
        
        print(f"✅ macOS应用已创建: {app_path}")
        
        # 询问是否移动到Applications文件夹
        try:
            import tkinter as tk
            from tkinter import messagebox
            
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            
            move_to_apps = messagebox.askyesno(
                "安装完成", 
                "是否将 'AI Circuit Denoiser' 移动到 Applications 文件夹？"
            )
            
            if move_to_apps:
                apps_path = Path("/Applications") / app_name
                if apps_path.exists():
                    apps_path.rename(Path("/Applications") / f"{app_name}.backup")
                
                import shutil
                shutil.move(str(app_path), "/Applications")
                print("✅ 应用已移动到 Applications 文件夹")
            
            root.destroy()
        except:
            print("💡 提示: 您可以手动将应用拖到 Applications 文件夹")
            
    except Exception as e:
        print(f"❌ 创建macOS应用失败: {e}")

def create_windows_shortcut():
    """创建Windows快捷方式"""
    try:
        import win32com.client
        import winshell
        
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, "AI Circuit Denoiser.lnk")
        
        # 获取Python解释器路径
        python_exe = sys.executable
        project_dir = Path(__file__).parent
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = python_exe
        shortcut.Arguments = '-m circuit_denoiser.main --desktop'
        shortcut.WorkingDirectory = str(project_dir)
        shortcut.Description = "AI Circuit Denoiser - AI-based circuit image denoising tool"
        shortcut.IconLocation = python_exe  # 使用Python图标
        
        shortcut.save()
        
        print(f"✅ Windows快捷方式已创建: {shortcut_path}")
        
    except ImportError:
        print("❌ 请安装依赖: pip install pywin32 winshell")
    except Exception as e:
        print(f"❌ 创建Windows快捷方式失败: {e}")

def create_linux_desktop():
    """创建Linux桌面文件"""
    try:
        project_dir = Path(__file__).parent
        
        desktop_file = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=AI Circuit Denoiser
Comment=AI-based circuit image denoising tool for electronics engineers
Exec=python3 -m circuit_denoiser.main --desktop
Path={project_dir}
Terminal=false
Categories=Graphics;Engineering;Science;
Keywords=circuit;denoise;ai;electronics;
Icon=python
StartupWMClass=circuit_denoiser
"""

        # 创建桌面文件
        desktop_path = Path.home() / "Desktop" / "ai-circuit-denoise.desktop"
        with open(desktop_path, 'w') as f:
            f.write(desktop_file)
        
        desktop_path.chmod(0o755)
        
        # 同时创建应用程序菜单项
        app_menu_path = Path.home() / ".local/share/applications/ai-circuit-denoise.desktop"
        app_menu_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(app_menu_path, 'w') as f:
            f.write(desktop_file)
        
        app_menu_path.chmod(0o755)
        
        print(f"✅ Linux桌面文件已创建: {desktop_path}")
        print(f"✅ 应用程序菜单项已创建: {app_menu_path}")
        
    except Exception as e:
        print(f"❌ 创建Linux桌面文件失败: {e}")

if __name__ == "__main__":
    create_desktop_shortcut()
