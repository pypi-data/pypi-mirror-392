"""测试启动 notepad 应用"""

import sys
import time
import platform
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app_launcher_mcp.apps import search_app_dynamically
from app_launcher_mcp.activator import open_app


def test_launch_notepad():
    """测试启动记事本"""
    if platform.system().lower() != "windows":
        print("❌ 此测试只能在 Windows 上运行")
        sys.exit(1)

    print("=" * 60)
    print("测试: 启动记事本")
    print("=" * 60)

    # 步骤 1: 搜索记事本
    print("\n步骤 1: 搜索记事本")
    app = search_app_dynamically("notepad")

    if not app:
        print("❌ 未找到记事本")
        sys.exit(1)

    print(f"✅ 找到记事本:")
    print(f"  名称: {app.name}")
    print(f"  路径: {app.path}")
    print(f"  进程名: {app.process_name}")

    # 步骤 2: 启动记事本
    print("\n步骤 2: 启动记事本")
    result = open_app(app)

    print(f"\n启动结果:")
    print(f"  成功: {result['success']}")
    print(f"  消息: {result['message']}")

    if result.get("steps"):
        print(f"\n执行步骤:")
        for i, step in enumerate(result["steps"], 1):
            print(f"  {i}. {step}")

    if result["success"]:
        print("\n✅ 测试通过")
        print("💡 提示: 请检查记事本是否已打开")

        # 等待几秒让用户看到记事本
        print("\n等待 3 秒...")
        time.sleep(3)

        # 尝试再次激活（测试激活已运行的应用）
        print("\n步骤 3: 再次激活记事本（测试激活已运行应用）")
        result2 = open_app(app)

        print(f"\n激活结果:")
        print(f"  成功: {result2['success']}")
        print(f"  消息: {result2['message']}")

        if result2.get("steps"):
            print(f"\n执行步骤:")
            for i, step in enumerate(result2["steps"], 1):
                print(f"  {i}. {step}")

        if result2["success"]:
            print("\n✅ 激活测试通过")
        else:
            print("\n⚠️ 激活测试失败（但这不一定是错误）")

    else:
        print("\n❌ 测试失败")
        sys.exit(1)


if __name__ == "__main__":
    test_launch_notepad()
