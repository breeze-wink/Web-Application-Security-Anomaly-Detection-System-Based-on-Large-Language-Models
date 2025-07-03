#!/usr/bin/env python3
"""
测试运行脚本
方便快速运行LogFileCapturer的功能测试
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """运行测试的主函数"""
    # 获取当前脚本所在目录
    test_dir = Path(__file__).parent
    backend_dir = test_dir.parent
    
    # 添加backend目录到Python路径
    sys.path.insert(0, str(backend_dir))
    
    print("🚀 开始运行 LogFileCapturer 功能测试...")
    print(f"📁 测试目录: {test_dir}")
    print(f"📁 后端目录: {backend_dir}")
    print("-" * 50)
    
    # 检查是否安装了pytest
    try:
        import pytest
        print("✅ pytest 已安装")
    except ImportError:
        print("❌ 未找到 pytest，请先安装:")
        print("   pip install pytest pytest-asyncio")
        return 1
    
    # 检查是否安装了pytest-asyncio
    try:
        import pytest_asyncio
        print("✅ pytest-asyncio 已安装")
    except ImportError:
        print("❌ 未找到 pytest-asyncio，请先安装:")
        print("   pip install pytest-asyncio")
        return 1
    
    # 切换到测试目录
    os.chdir(test_dir)
    
    # 构建pytest命令
    pytest_args = [
        sys.executable, "-m", "pytest",
        "test_log_capturer.py",
        "-v",  # 详细输出
        "--tb=short",  # 简短的错误追踪
        "--durations=10",  # 显示最慢的10个测试
        "-s",  # 不捕获输出，可以看到print语句
        "--color=yes"  # 彩色输出
    ]
    
    print("🧪 执行测试命令:")
    print(f"   {' '.join(pytest_args)}")
    print("-" * 50)
    
    # 运行测试
    try:
        result = subprocess.run(pytest_args, cwd=test_dir)
        
        print("-" * 50)
        if result.returncode == 0:
            print("🎉 所有测试通过！")
            print("✅ LogFileCapturer 功能正常")
        else:
            print("❌ 某些测试失败")
            print("🔍 请检查上面的错误信息")
        
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
        return 130
    except Exception as e:
        print(f"❌ 运行测试时发生错误: {e}")
        return 1

def run_specific_test(test_name: str):
    """运行特定的测试"""
    test_dir = Path(__file__).parent
    
    pytest_args = [
        sys.executable, "-m", "pytest",
        "test_log_capturer.py",
        "-v", "-s",
        "-k", test_name  # 只运行匹配名称的测试
    ]
    
    print(f"🧪 运行特定测试: {test_name}")
    print("-" * 50)
    
    result = subprocess.run(pytest_args, cwd=test_dir)
    return result.returncode

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 如果提供了参数，运行特定测试
        test_name = sys.argv[1]
        exit_code = run_specific_test(test_name)
    else:
        # 运行所有测试
        exit_code = main()
    
    sys.exit(exit_code) 