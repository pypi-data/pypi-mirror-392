"""测试 Windows 平台的动态搜索功能"""

import sys
import platform
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app_launcher_mcp.apps import (
    search_app_dynamically,
    _windows_where_search,
    _windows_startmenu_search,
)


def test_where_command():
    """测试 where 命令搜索"""
    print("=" * 60)
    print("测试 1: where 命令搜索")
    print("=" * 60)

    # 测试系统内置应用
    test_apps = ["notepad", "calc", "cmd", "powershell"]

    for app_name in test_apps:
        print(f"\n搜索: {app_name}")
        result = _windows_where_search(app_name)

        if result:
            print(f"  ✅ 找到: {result.path}")
            print(f"  进程名: {result.process_name}")
        else:
            print(f"  ❌ 未找到")


def test_where_with_exe():
    """测试带 .exe 后缀的搜索"""
    print("\n" + "=" * 60)
    print("测试 2: 带 .exe 后缀的搜索")
    print("=" * 60)

    test_apps = ["notepad.exe", "calc.exe"]

    for app_name in test_apps:
        print(f"\n搜索: {app_name}")
        result = _windows_where_search(app_name)

        if result:
            print(f"  ✅ 找到: {result.path}")
        else:
            print(f"  ❌ 未找到")


def test_dynamic_search():
    """测试完整的动态搜索流程"""
    print("\n" + "=" * 60)
    print("测试 3: 完整动态搜索")
    print("=" * 60)

    # Windows 内置应用
    test_apps = ["记事本", "notepad", "计算器", "calc"]

    for app_name in test_apps:
        print(f"\n搜索: {app_name}")
        result = search_app_dynamically(app_name)

        if result:
            print(f"  ✅ 找到: {result.name}")
            print(f"  路径: {result.path}")
            print(f"  进程名: {result.process_name}")
        else:
            print(f"  ❌ 未找到")


def test_common_apps():
    """测试常见应用搜索"""
    print("\n" + "=" * 60)
    print("测试 4: 常见应用搜索")
    print("=" * 60)

    # 这些应用可能存在也可能不存在
    test_apps = ["微信", "wechat", "qq", "chrome", "edge", "vscode"]

    for app_name in test_apps:
        print(f"\n搜索: {app_name}")
        result = search_app_dynamically(app_name)

        if result:
            print(f"  ✅ 找到: {result.name}")
            print(f"  路径: {result.path}")
            print(f"  进程名: {result.process_name}")
        else:
            print(f"  ℹ️ 未找到 (可能未安装)")


def main():
    """运行所有测试"""
    if platform.system().lower() != "windows":
        print("❌ 此测试只能在 Windows 上运行")
        sys.exit(1)

    print("开始 Windows 动态搜索测试\n")

    try:
        test_where_command()
        test_where_with_exe()
        test_dynamic_search()
        test_common_apps()

        print("\n" + "=" * 60)
        print("✅ 所有测试完成")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
