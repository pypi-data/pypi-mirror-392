"""测试 where 命令功能"""

import sys
import subprocess
import platform
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app_launcher_mcp.apps import _windows_where_search


def test_where_command_raw():
    """测试原始 where 命令"""
    if platform.system().lower() != "windows":
        print("❌ 此测试只能在 Windows 上运行")
        sys.exit(1)

    print("=" * 60)
    print("测试: where 命令原始输出")
    print("=" * 60)

    test_commands = ["notepad", "calc", "cmd", "powershell", "python"]

    for cmd in test_commands:
        print(f"\n执行: where {cmd}")

        try:
            result = subprocess.run(
                ["where", cmd],
                capture_output=True,
                text=True,
                timeout=3,
                encoding='utf-8',
                errors='ignore'
            )

            if result.returncode == 0:
                print(f"  ✅ 返回码: {result.returncode}")
                print(f"  输出:")
                for line in result.stdout.strip().split("\n"):
                    print(f"    - {line}")
            else:
                print(f"  ❌ 返回码: {result.returncode}")
                print(f"  错误: {result.stderr.strip()}")

        except subprocess.TimeoutExpired:
            print(f"  ⏱️ 超时")
        except Exception as e:
            print(f"  ❌ 异常: {e}")


def test_where_search_function():
    """测试封装的 where 搜索函数"""
    print("\n" + "=" * 60)
    print("测试: _windows_where_search 函数")
    print("=" * 60)

    test_apps = ["notepad", "calc", "python", "nonexistent"]

    for app in test_apps:
        print(f"\n搜索: {app}")
        result = _windows_where_search(app)

        if result:
            print(f"  ✅ 找到:")
            print(f"    名称: {result.name}")
            print(f"    路径: {result.path}")
            print(f"    进程名: {result.process_name}")
            print(f"    路径存在: {Path(result.path).exists()}")
        else:
            print(f"  ℹ️ 未找到")


def test_encoding():
    """测试编码处理"""
    print("\n" + "=" * 60)
    print("测试: 编码处理")
    print("=" * 60)

    # 测试中文应用名
    test_apps = ["记事本", "计算器"]

    for app in test_apps:
        print(f"\n搜索: {app}")

        try:
            result = subprocess.run(
                ["where", app],
                capture_output=True,
                text=True,
                timeout=3,
                encoding='utf-8',
                errors='ignore'
            )

            print(f"  返回码: {result.returncode}")

            if result.stdout:
                print(f"  stdout (前100字符): {result.stdout[:100]}")

            if result.stderr:
                print(f"  stderr: {result.stderr[:100]}")

        except Exception as e:
            print(f"  异常: {e}")


if __name__ == "__main__":
    test_where_command_raw()
    test_where_search_function()
    test_encoding()

    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
