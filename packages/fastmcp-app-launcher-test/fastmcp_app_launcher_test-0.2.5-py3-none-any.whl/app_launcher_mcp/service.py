"""封装应用注册表与激活器的业务逻辑。"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List

from .activator import open_app as activate_app
from .apps import AppRegistry, build_registry, resolve_windows_shortcut, search_app_dynamically

logger = logging.getLogger(__name__)


class AppLauncherService:
    """管理应用配置并通过激活器打开应用。"""

    def __init__(self, auto_discover: bool = True) -> None:
        self.auto_discover = auto_discover
        self.registry: AppRegistry = build_registry(auto_discover=auto_discover)

    def reload(self) -> None:
        self.registry = build_registry(auto_discover=self.auto_discover)

    def list_apps(self) -> List[dict[str, Any]]:
        return self.registry.dump()

    def debug_app(self, app_name: str) -> Dict[str, Any]:
        """调试应用状态（仅 Windows）"""
        app = self.registry.find(app_name)
        if not app:
            raise ValueError(f"未找到匹配的应用: {app_name}")
        
        # 返回应用基本信息，不调用不存在的函数
        import os
        info: Dict[str, Any] = {
            "name": app.name,
            "path": app.path,
            "exists": os.path.exists(app.path),
            "keywords": app.keywords,
            "hotkey": app.hotkey,
            "process_name": app.process_name,
        }
        if app.path.lower().endswith(".lnk"):
            info["shortcut_target"] = resolve_windows_shortcut(app.path)
        return info

    async def open_app(self, query: str) -> Dict[str, Any]:
        """打开应用 - 优先使用注册表，找不到时使用动态搜索"""
        # 步骤1: 尝试从注册表查找
        app = self.registry.find(query)

        # 步骤2: 如果注册表找不到，使用动态搜索
        if not app:
            logger.info(f"注册表未找到应用 '{query}'，启动动态搜索")
            app = search_app_dynamically(query)

            if not app:
                raise ValueError(
                    f"未找到匹配的应用: {query}\n"
                    f"已搜索范围:\n"
                    f"  - 配置文件中的应用\n"
                    f"  - 系统自动发现的应用\n"
                    f"  - PATH 环境变量中的可执行文件\n"
                    f"  - Start Menu 快捷方式 (Windows)\n"
                    f"  - 常见安装路径\n"
                    f"请检查应用名称是否正确或应用是否已安装"
                )

            logger.info(f"动态搜索找到应用: {app.name} -> {app.path}")

        # 步骤3: 使用激活器打开应用
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, activate_app, app)

        payload = {
            "query": query,
            "app": {
                "name": app.name,
                "path": app.path,
                "keywords": app.keywords,
                "hotkey": app.hotkey,
            },
            "execution": result,
        }

        if not result.get("success"):
            raise RuntimeError(f"打开应用失败: {result.get('message')}")
        return payload
