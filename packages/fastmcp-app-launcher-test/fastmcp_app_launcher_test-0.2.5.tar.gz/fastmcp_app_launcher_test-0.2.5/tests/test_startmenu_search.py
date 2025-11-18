"""测试 Start Menu 搜索功能"""

import sys
import platform
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app_launcher_mcp.apps import (
    _windows_startmenu_search,
    WINDOWS_SHORTCUT_DIRS,
)


def test_startmenu_dirs():
    """测试 Start Menu 目录"""
    if platform.system().lower() != "windows":
        print("❌ 此测试只能在 Windows 上运行")
        sys.exit(1)

    print("=" * 60)
    print("测试: Start Menu 目录")
    print("=" * 60)

    for i, dir_path in enumerate(WINDOWS_SHORTCUT_DIRS, 1):
        print(f"\n{i}. {dir_path}")
        print(f"   存在: {dir_path.exists()}")

        if dir_path.exists():
            # 统计 .lnk 文件数量
            try:
                lnk_files = list(dir_path.rglob("*.lnk"))
                print(f"   快捷方式数量: {len(lnk_files)}")

                # 显示前 5 个
                print(f"   示例快捷方式:")
                for lnk in lnk_files[:5]:
                    print(f"     - {lnk.name}")

            except PermissionError:
                print(f"   ⚠️ 权限不足")
            except Exception as e:
                print(f"   ❌ 错误: {e}")


def test_startmenu_search():
    """测试 Start Menu 搜索"""
    print("\n" + "=" * 60)
    print("测试: Start Menu 搜索")
    print("=" * 60)

    # 测试常见应用
    test_apps = [
        "notepad",      # 记事本可能没有快捷方式
        "edge",         # Microsoft Edge
        "chrome",       # Chrome (如果安装了)
        "微信",          # 微信 (如果安装了)
        "qq",           # QQ (如果安装了)
    ]

    for app_name in test_apps:
        print(f"\n搜索: {app_name}")
        result = _windows_startmenu_search(app_name)

        if result:
            print(f"  ✅ 找到:")
            print(f"    名称: {result.name}")
            print(f"    路径: {result.path}")
            print(f"    进程名: {result.process_name}")
            print(f"    关键词: {result.keywords}")
        else:
            print(f"  ℹ️ 未找到 (可能未安装或无快捷方式)")


def test_list_all_shortcuts():
    """列出所有快捷方式（前 20 个）"""
    print("\n" + "=" * 60)
    print("测试: 列出所有快捷方式")
    print("=" * 60)

    all_shortcuts = []

    for base_dir in WINDOWS_SHORTCUT_DIRS:
        if not base_dir.exists():
            continue

        try:
            shortcuts = list(base_dir.rglob("*.lnk"))
            all_shortcuts.extend(shortcuts[:10])  # 每个目录最多 10 个
        except Exception as e:
            print(f"⚠️ 无法访问 {base_dir}: {e}")

    print(f"\n找到 {len(all_shortcuts)} 个快捷方式（显示前 20 个）:\n")

    for i, shortcut in enumerate(all_shortcuts[:20], 1):
        print(f"{i:2d}. {shortcut.stem}")


if __name__ == "__main__":
    test_startmenu_dirs()
    test_startmenu_search()
    test_list_all_shortcuts()

    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
