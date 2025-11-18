"""测试快捷方式解析功能"""

import sys
import platform
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app_launcher_mcp.apps import (
    resolve_windows_shortcut,
    _process_name_from_shortcut,
    WINDOWS_SHORTCUT_DIRS,
)


def test_shortcut_resolution():
    """测试快捷方式解析"""
    if platform.system().lower() != "windows":
        print("❌ 此测试只能在 Windows 上运行")
        sys.exit(1)

    print("=" * 60)
    print("测试: 快捷方式解析")
    print("=" * 60)

    # 查找一些快捷方式进行测试
    shortcuts = []

    for base_dir in WINDOWS_SHORTCUT_DIRS:
        if not base_dir.exists():
            continue

        try:
            found = list(base_dir.rglob("*.lnk"))
            shortcuts.extend(found[:5])  # 每个目录最多 5 个
            if len(shortcuts) >= 10:
                break
        except Exception:
            pass

    if not shortcuts:
        print("⚠️ 未找到任何快捷方式")
        return

    print(f"\n找到 {len(shortcuts)} 个快捷方式进行测试:\n")

    for i, shortcut in enumerate(shortcuts[:10], 1):
        print(f"{i}. {shortcut.name}")
        print(f"   路径: {shortcut}")

        # 解析目标
        target = resolve_windows_shortcut(shortcut)
        if target:
            print(f"   ✅ 目标: {target}")
            print(f"   目标存在: {Path(target).exists()}")
        else:
            print(f"   ❌ 解析失败")

        # 获取进程名
        process_name = _process_name_from_shortcut(shortcut)
        if process_name:
            print(f"   进程名: {process_name}")
        else:
            print(f"   ⚠️ 无法推断进程名")

        print()


def test_pywin32_availability():
    """测试 pywin32 是否可用"""
    print("=" * 60)
    print("测试: pywin32 可用性")
    print("=" * 60)

    try:
        import pythoncom
        from win32com.client import Dispatch

        print("\n✅ pythoncom 可用")
        print(f"   版本: {pythoncom.__file__}")

        # 测试初始化
        try:
            pythoncom.CoInitialize()
            print("✅ CoInitialize 成功")
            pythoncom.CoUninitialize()
        except Exception as e:
            print(f"⚠️ CoInitialize 失败: {e}")

        # 测试 WScript.Shell
        try:
            shell = Dispatch("WScript.Shell")
            print("✅ WScript.Shell 可用")
        except Exception as e:
            print(f"❌ WScript.Shell 失败: {e}")

    except ImportError as e:
        print(f"❌ pywin32 未安装: {e}")
        print("\n请安装:")
        print("  pip install pywin32")


if __name__ == "__main__":
    test_pywin32_availability()
    print()
    test_shortcut_resolution()

    print("=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
