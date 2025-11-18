#!/usr/bin/env python3
"""
测试修复后的导入
"""

print("测试导入...")

try:
    from circuit_denoiser.model import load_model
    print("✅ model.load_model 导入成功")
    
    # 测试创建模型
    model = load_model()
    print(f"✅ 模型创建成功，参数数量: {sum(p.numel() for p in model.parameters())}")
    
except ImportError as e:
    print(f"❌ model.load_model 导入失败: {e}")

try:
    from circuit_denoiser import load_model
    print("✅ package.load_model 导入成功")
except ImportError as e:
    print(f"❌ package.load_model 导入失败: {e}")

try:
    from circuit_denoiser.main import main
    print("✅ main 导入成功")
except ImportError as e:
    print(f"❌ main 导入失败: {e}")

print("测试完成!")
