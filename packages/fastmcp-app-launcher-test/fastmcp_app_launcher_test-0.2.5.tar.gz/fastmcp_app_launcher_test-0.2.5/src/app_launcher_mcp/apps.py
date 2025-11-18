"""应用配置加载与搜索逻辑。"""

from __future__ import annotations

import json
import logging
import os
import platform
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Sequence, Optional

logger = logging.getLogger(__name__)


def _package_root() -> Path:
    """推断项目根目录，便于默认查找示例配置。"""

    current = Path(__file__).resolve()
    try:
        return current.parents[2]
    except IndexError:
        return current.parent

PACKAGE_ROOT = _package_root()

DEFAULT_CONFIG_PATHS = (
    Path.home() / ".mcp-apps.json",
    Path.cwd() / "mcp-apps.json",
    Path.home() / ".config" / "mcp-apps" / "config.json",
    PACKAGE_ROOT / "mcp-apps.json",
    PACKAGE_ROOT / "mcp-apps.example.json",
    Path.cwd() / "mcp-apps.example.json",
)

AUTO_DISCOVER_LIMIT = int(os.environ.get("MCP_AUTO_DISCOVER_LIMIT", "200"))

_PLATFORM_ALIASES = {
    "windows": {"windows", "win32", "win"},
    "macos": {"macos", "mac", "darwin", "osx"},
    "linux": {"linux", "gnu/linux", "gnu"},
}


def _normalize_platform_key(value: str | None) -> str | None:
    if not value:
        return None
    token = value.strip().lower()
    if not token:
        return None
    for canonical, aliases in _PLATFORM_ALIASES.items():
        if token == canonical or token in aliases:
            return canonical
    return token


CURRENT_PLATFORM = _normalize_platform_key(platform.system()) or platform.system().lower()


def _paths_from_env(env_name: str, defaults: Sequence[str]) -> tuple[Path, ...]:
    raw = os.environ.get(env_name)
    entries = raw.split(os.pathsep) if raw else defaults
    resolved: list[Path] = []
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        resolved.append(Path(entry).expanduser())
    return tuple(resolved)


def _config_paths_override() -> tuple[Path, ...]:
    raw = os.environ.get("MCP_APP_CONFIG")
    if not raw:
        return ()
    entries = [segment.strip() for segment in raw.split(os.pathsep) if segment.strip()]
    return tuple(Path(entry).expanduser() for entry in entries)


def _normalize_path(raw: str) -> str:
    """展开 ~ 与环境变量，返回规范化路径字符串。"""

    expanded = os.path.expandvars(raw.strip())
    path_obj = Path(expanded).expanduser()
    return str(path_obj.resolve()) if path_obj.anchor or path_obj.exists() else str(path_obj)


def _platform_list_matches(values: Iterable[str] | None) -> bool:
    """判断 platforms 列表是否包含当前系统。"""

    if values is None:
        return True
    normalized = {
        normalized
        for item in values
        if (normalized := _normalize_platform_key(str(item)))
    }
    if not normalized:
        return True
    return CURRENT_PLATFORM in normalized


def _select_platform_path(data: dict) -> str | None:
    """根据 platform_paths 或 paths 字段推断当前系统路径。"""

    platform_paths = data.get("platform_paths")
    if isinstance(platform_paths, dict):
        default_candidate: str | None = None
        for raw_key, raw_path in platform_paths.items():
            normalized_key = _normalize_platform_key(str(raw_key))
            path_value = str(raw_path).strip() if raw_path else ""
            if not path_value:
                continue
            if normalized_key == CURRENT_PLATFORM:
                return path_value
            lowered = str(raw_key).strip().lower()
            if lowered in {"default", "any", "*"} and not default_candidate:
                default_candidate = path_value
        if default_candidate:
            return default_candidate

    paths_field = data.get("paths")
    if isinstance(paths_field, list):
        preferred: list[str] = []
        fallback: list[str] = []
        for entry in paths_field:
            entry_path: str | None = None
            platforms = None
            if isinstance(entry, str):
                entry_path = entry.strip()
            elif isinstance(entry, dict):
                raw_path = entry.get("path")
                if raw_path:
                    entry_path = str(raw_path).strip()
                platforms_raw = entry.get("platforms")
                if isinstance(platforms_raw, str):
                    platforms = [platforms_raw]
                else:
                    platforms = platforms_raw
            if not entry_path:
                continue
            if platforms is None:
                fallback.append(entry_path)
            elif _platform_list_matches(platforms):
                preferred.append(entry_path)
        if preferred:
            return preferred[0]
        if fallback:
            return fallback[0]

    return None

# Windows 默认应用（使用 os.path.join 或 Path 规范化路径）
DEFAULT_WINDOWS_APPS = (
    {
        "name": "QQ",
        "paths": [
            r"C:\Program Files\Tencent\QQ\Bin\QQ.exe",
            r"C:\Program Files (x86)\Tencent\QQ\Bin\QQ.exe",
            os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", "Tencent", "QQ", "Bin", "QQ.exe"),
        ],
        "keywords": ["qq", "tencent", "腾讯"],
        "hotkey": "Ctrl+Alt+Z",
        "relaunch_when_tray_hidden": True,
        "shell_fallback_on_fail": True,
        "process_name": "QQ.exe",
    },
    {
        "name": "微信",
        "paths": [
            r"C:\Program Files\Tencent\WeChat\WeChat.exe",
            r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
            os.path.join(os.environ.get("USERPROFILE", ""), "AppData", "Local", "Tencent", "WeChat", "WeChat.exe"),
        ],
        "keywords": ["微信", "wechat", "weixin"],
        "hotkey": "Ctrl+Alt+W",
        "relaunch_when_tray_hidden": True,
        "shell_fallback_on_fail": True,
        "process_name": "WeChat.exe",
    },
    {
        "name": "Visual Studio Code",
        "paths": [
            r"C:\Program Files\Microsoft VS Code\Code.exe",
            r"C:\Users\Public\scoop\apps\vscode\current\code.exe",
        ],
        "keywords": ["vscode", "code", "编辑器"],
        "shell_fallback_on_fail": True,
    },
)

DEFAULT_MAC_APPS = (
    {
        "name": "WeChat",
        "path": "/Applications/WeChat.app",
        "keywords": ["wechat", "微信"],
    },
    {
        "name": "Safari",
        "path": "/Applications/Safari.app",
        "keywords": ["safari", "browser", "浏览器"],
    },
    {
        "name": "iTerm",
        "path": "/Applications/iTerm.app",
        "keywords": ["terminal", "iterm"],
    },
)

MAC_APPLICATION_DIRS = _paths_from_env(
    "MCP_MAC_APP_DIRS",
    [
        "/Applications",
        "/Applications/Utilities",
        "/System/Applications",
        "~/Applications",
    ],
)

WINDOWS_SHORTCUT_DEFAULTS = [
    Path(os.environ.get("ProgramData", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
    Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs",
]

# 修复：先检查环境变量是否存在，再调用 split()
_windows_shortcut_env = os.environ.get("MCP_WINDOWS_SHORTCUT_DIRS")
WINDOWS_SHORTCUT_DIRS = tuple(
    Path(entry).expanduser()
    for entry in (
        _windows_shortcut_env.split(os.pathsep)
        if _windows_shortcut_env
        else [
            str(path)
            for path in WINDOWS_SHORTCUT_DEFAULTS
            if path and str(path).strip() not in {"", "."}
        ]
    )
    if entry.strip()
)

WINDOWS_SHORTCUT_IGNORE_KEYWORDS = {
    "uninstall",
    "卸载",
    "官网",
    "website",
    "help",
    "manual",
    "readme",
}


def resolve_windows_shortcut(shortcut: str | Path) -> str | None:
    """解析 Windows .lnk，返回目标路径。"""

    if platform.system().lower() != "windows":
        return None

    try:
        import pythoncom  # type: ignore
        from win32com.client import Dispatch  # type: ignore
    except Exception:
        return None

    shortcut_path = str(shortcut)
    initialized = False
    try:
        pythoncom.CoInitialize()
        initialized = True
    except Exception:
        # 已初始化或不可用，继续尝试
        pass

    try:
        shell = Dispatch("WScript.Shell")
        link = shell.CreateShortcut(shortcut_path)
        target = link.Targetpath  # type: ignore[attr-defined]
        if target:
            return _normalize_path(target)
        return None
    except Exception:
        return None
    finally:
        if initialized:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass


def _process_name_from_shortcut(shortcut: Path) -> str | None:
    target = resolve_windows_shortcut(shortcut)
    if not target:
        return None
    target_path = Path(target)
    name = target_path.name
    if not name:
        return None
    if target_path.suffix:
        return name
    return f"{target_path.stem}.exe"


def _should_skip_shortcut(name: str) -> bool:
    lowered = name.lower().strip()
    if not lowered:
        return True
    return any(keyword in lowered for keyword in WINDOWS_SHORTCUT_IGNORE_KEYWORDS)


@dataclass(slots=True)
class AppInfo:
    """单个应用的元数据。"""

    name: str
    path: str
    keywords: List[str] = field(default_factory=list)
    hotkey: str | None = None
    # 当检测到窗口隐藏在系统托盘且未最小化时，尝试通过 Shell 再次“打开”以唤起主窗体
    relaunch_when_tray_hidden: bool = False
    # 所有激活方法失败后，最后再通过 Shell 打开一次作为兜底
    shell_fallback_on_fail: bool = False
    # 为特殊应用显式指定进程名，避免依赖 .lnk 名称
    process_name: str | None = None

    def score(self, query: str) -> int:
        """为匹配打分，用于找到最优应用。"""

        q = query.lower().strip()
        if not q:
            return 0

        name = self.name.lower()
        score = 0
        if name == q:
            return 100
        if name.startswith(q):
            score = max(score, 90)
        if q in name:
            score = max(score, 70)

        for kw in self.keywords:
            k = kw.lower()
            if k == q:
                score = max(score, 80)
            elif k.startswith(q):
                score = max(score, 60)
            elif q in k:
                score = max(score, 40)

        return score


class AppRegistry:
    """应用注册表，负责搜索与序列化。"""

    def __init__(self, apps: Sequence[AppInfo] | None = None) -> None:
        self._apps: List[AppInfo] = []
        if apps:
            self.extend(apps)

    @property
    def apps(self) -> List[AppInfo]:
        return list(self._apps)

    def extend(self, apps: Sequence[AppInfo]) -> None:
        for app in apps:
            self.add(app)

    def add(self, app: AppInfo) -> None:
        if not app.name or not app.path:
            return
        lower = app.name.lower()
        if any(existing.name.lower() == lower or existing.path == app.path for existing in self._apps):
            return
        self._apps.append(app)

    def find(self, query: str) -> AppInfo | None:
        candidates = [
            (app, app.score(query))
            for app in self._apps
        ]
        candidates = [item for item in candidates if item[1] > 0]
        candidates.sort(key=lambda item: item[1], reverse=True)
        return candidates[0][0] if candidates else None

    def dump(self) -> List[dict]:
        return [
            {
                "name": app.name,
                "path": app.path,
                "keywords": app.keywords,
                "hotkey": app.hotkey,
                "relaunch_when_tray_hidden": app.relaunch_when_tray_hidden,
                "shell_fallback_on_fail": app.shell_fallback_on_fail,
                "process_name": app.process_name,
            }
            for app in self._apps
        ]


def _clean_keywords(value: Iterable[str] | None) -> List[str]:
    if not value:
        return []
    return sorted({kw.strip() for kw in value if kw and kw.strip()})


def _keywords_from_name(name: str) -> List[str]:
    tokens = {name, name.lower()}
    normalized = name.replace("_", " ").replace("-", " ")
    tokens.update(part for part in normalized.split() if part)
    return _clean_keywords(tokens)


def _app_from_mapping(data: dict) -> AppInfo | None:
    name = str(data.get("name", "")).strip()
    default_path = str(data.get("path", "")).strip()
    platform_path = _select_platform_path(data)
    chosen_path = platform_path or default_path
    if not name or not chosen_path:
        return None
    normalized_path = _normalize_path(chosen_path)
    keywords = data.get("keywords", [])
    hotkey = data.get("hotkey")
    relaunch_when_tray_hidden = bool(data.get("relaunch_when_tray_hidden", False))
    shell_fallback_on_fail = bool(data.get("shell_fallback_on_fail", False))
    process_name = data.get("process_name")
    if process_name:
        process_name = str(process_name).strip() or None
    return AppInfo(
        name=name,
        path=normalized_path,
        keywords=_clean_keywords(keywords),
        hotkey=hotkey,
        relaunch_when_tray_hidden=relaunch_when_tray_hidden,
        shell_fallback_on_fail=shell_fallback_on_fail,
        process_name=process_name,
    )


def load_from_env(var: str = "MCP_APPS") -> List[AppInfo]:
    raw = os.environ.get(var)
    if not raw:
        return []

    raw = raw.strip()
    apps: List[AppInfo] = []
    try:
        if raw.startswith("["):
            parsed = json.loads(raw)
            for item in parsed:
                app = _app_from_mapping(item)
                if app:
                    apps.append(app)
        else:
            entries = [segment.strip() for segment in raw.split("|") if segment.strip()]
            for entry in entries:
                parts = [p.strip() for p in entry.split(";")]
                if len(parts) < 2:
                    continue
                name, app_path = parts[:2]
                app_path = _normalize_path(app_path)
                keywords = parts[2].split(",") if len(parts) > 2 else []
                hotkey = parts[3] if len(parts) > 3 else None
                process_name = parts[4] if len(parts) > 4 else None
                process_name = process_name or None
                app = AppInfo(
                    name=name,
                    path=app_path,
                    keywords=_clean_keywords(keywords),
                    hotkey=hotkey,
                    process_name=process_name,
                )
                apps.append(app)
    except json.JSONDecodeError as exc:
        raise ValueError(f"无法解析环境变量 {var}: {exc}") from exc

    return apps


def load_from_config(paths: Sequence[Path] = DEFAULT_CONFIG_PATHS) -> List[AppInfo]:
    candidates: tuple[Path, ...] = _config_paths_override() + tuple(paths)
    for path in candidates:
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"配置文件 {path} 解析失败: {exc}") from exc

        payload = data.get("apps", []) if isinstance(data, dict) else data
        apps = [_app_from_mapping(item) for item in payload]
        return [app for app in apps if app]
    return []


def _discover_windows_shortcuts(limit: int | None = None) -> List[AppInfo]:
    apps: List[AppInfo] = []
    max_items = limit or AUTO_DISCOVER_LIMIT
    for base in WINDOWS_SHORTCUT_DIRS:
        if not base or not base.exists():
            continue
        for shortcut in base.rglob("*.lnk"):
            name = shortcut.stem.strip()
            if not name or _should_skip_shortcut(name):
                continue
            process_name = _process_name_from_shortcut(shortcut)
            apps.append(
                AppInfo(
                    name=name,
                    path=str(shortcut),
                    keywords=_keywords_from_name(name),
                    relaunch_when_tray_hidden=True,
                    shell_fallback_on_fail=True,
                    process_name=process_name,
                )
            )
            if len(apps) >= max_items:
                return apps
    return apps


def discover_windows_apps(limit: int | None = None) -> List[AppInfo]:
    if platform.system().lower() != "windows":
        return []

    max_items = limit or AUTO_DISCOVER_LIMIT
    discovered: List[AppInfo] = []
    for entry in DEFAULT_WINDOWS_APPS:
        if len(discovered) >= max_items:
            return discovered
        paths = entry.get("paths", [])
        if isinstance(paths, str):
            paths = [paths]
        for candidate in paths:
            if candidate and Path(candidate).exists():
                app = AppInfo(
                    name=entry["name"],
                    path=candidate,
                    keywords=_clean_keywords(entry.get("keywords")),
                    hotkey=entry.get("hotkey"),
                    relaunch_when_tray_hidden=bool(entry.get("relaunch_when_tray_hidden", False)),
                    shell_fallback_on_fail=bool(entry.get("shell_fallback_on_fail", False)),
                    process_name=entry.get("process_name"),
                )
                discovered.append(app)
                break

    # Start Menu 快捷方式扫描
    remaining = max_items - len(discovered)
    if remaining > 0 and WINDOWS_SHORTCUT_DIRS:
        discovered.extend(_discover_windows_shortcuts(limit=remaining))
    return discovered


def discover_macos_apps(limit: int | None = None) -> List[AppInfo]:
    if platform.system().lower() != "darwin":
        return []

    max_items = limit or AUTO_DISCOVER_LIMIT
    apps: List[AppInfo] = []
    seen_paths: set[str] = set()

    def add_app(info: AppInfo) -> None:
        if info.path in seen_paths:
            return
        seen_paths.add(info.path)
        apps.append(info)

    # 先加入内置常用应用，保证最小可用集合
    for entry in DEFAULT_MAC_APPS:
        candidate = entry["path"]
        if Path(candidate).exists():
            add_app(
                AppInfo(
                    name=entry["name"],
                    path=candidate,
                    keywords=_clean_keywords(entry.get("keywords")),
                )
            )
            if len(apps) >= max_items:
                return apps

    # 遍历常见应用目录
    for base in MAC_APPLICATION_DIRS:
        if not base.exists():
            continue
        for app_dir in base.rglob("*.app"):
            if ".app/Contents/" in str(app_dir):
                continue
            if not app_dir.is_dir():
                continue
            add_app(
                AppInfo(
                    name=app_dir.stem,
                    path=str(app_dir),
                    keywords=_keywords_from_name(app_dir.stem),
                )
            )
            if len(apps) >= max_items:
                return apps
    return apps


def build_registry(auto_discover: bool = True) -> AppRegistry:
    registry = AppRegistry()
    registry.extend(load_from_config())
    registry.extend(load_from_env())

    if auto_discover:
        registry.extend(discover_windows_apps())
        registry.extend(discover_macos_apps())

    return registry


# ============================================================================
# 动态应用搜索功能（不依赖配置文件路径）
# ============================================================================

def search_app_dynamically(app_name: str) -> Optional[AppInfo]:
    """
    动态搜索应用程序，不依赖配置文件中的路径。

    根据应用名称在系统中实时搜索：
    - Windows: 使用 where 命令、Start Menu 搜索
    - macOS: 使用 mdfind (Spotlight) 或 open -a
    - Linux: 使用 which 命令

    Args:
        app_name: 应用名称（如 "微信", "Chrome", "VS Code"）

    Returns:
        AppInfo 对象，如果找不到则返回 None
    """
    logger.info(f"开始动态搜索应用: {app_name}")

    if CURRENT_PLATFORM == "windows":
        return _search_windows_app_dynamic(app_name)
    elif CURRENT_PLATFORM == "macos":
        return _search_macos_app_dynamic(app_name)
    elif CURRENT_PLATFORM == "linux":
        return _search_linux_app_dynamic(app_name)
    else:
        logger.warning(f"不支持的平台: {CURRENT_PLATFORM}")
        return None


def _search_windows_app_dynamic(app_name: str) -> Optional[AppInfo]:
    """Windows 平台动态搜索应用"""
    query = app_name.strip()

    # 策略1: 使用 where 命令查找 PATH 中的可执行文件
    logger.debug(f"策略1: 使用 where 命令查找 '{query}'")
    result = _windows_where_search(query)
    if result:
        return result

    # 策略2: 尝试添加 .exe 后缀再搜索
    if not query.lower().endswith(".exe"):
        logger.debug(f"策略2: 使用 where 命令查找 '{query}.exe'")
        result = _windows_where_search(f"{query}.exe")
        if result:
            return result

    # 策略3: 搜索 Start Menu 快捷方式（实时搜索，不缓存）
    logger.debug(f"策略3: 搜索 Start Menu 快捷方式")
    result = _windows_startmenu_search(query)
    if result:
        return result

    # 策略4: 尝试常见安装路径
    logger.debug(f"策略4: 搜索常见安装路径")
    result = _windows_common_paths_search(query)
    if result:
        return result

    logger.warning(f"Windows 平台未找到应用: {app_name}")
    return None


def _windows_where_search(query: str) -> Optional[AppInfo]:
    """使用 where 命令查找可执行文件"""
    try:
        # 尝试使用系统默认编码
        result = subprocess.run(
            ["where", query],
            capture_output=True,
            text=True,
            timeout=3,
            encoding='utf-8',  # 明确指定 UTF-8 编码
            errors='ignore',   # 忽略无法解码的字符
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )

        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            first_path = lines[0].strip()

            if first_path and Path(first_path).exists():
                logger.info(f"通过 where 命令找到: {first_path}")

                # 提取进程名
                process_name = Path(first_path).name

                return AppInfo(
                    name=query.replace(".exe", ""),
                    path=first_path,
                    keywords=[query.lower(), query.replace(".exe", "").lower()],
                    relaunch_when_tray_hidden=True,
                    shell_fallback_on_fail=True,
                    process_name=process_name,
                )
    except subprocess.TimeoutExpired:
        logger.warning(f"where 命令超时: {query}")
    except Exception as e:
        logger.debug(f"where 命令失败: {e}")

    return None


def _windows_startmenu_search(query: str) -> Optional[AppInfo]:
    """搜索 Start Menu 快捷方式"""
    query_lower = query.lower()

    for base_dir in WINDOWS_SHORTCUT_DIRS:
        if not base_dir.exists():
            continue

        try:
            # 遍历所有 .lnk 文件
            for shortcut in base_dir.rglob("*.lnk"):
                try:
                    name = shortcut.stem.strip()

                    # 模糊匹配
                    if query_lower in name.lower():
                        if _should_skip_shortcut(name):
                            continue

                        logger.info(f"在 Start Menu 找到: {shortcut}")
                        process_name = _process_name_from_shortcut(shortcut)

                        return AppInfo(
                            name=name,
                            path=str(shortcut),
                            keywords=_keywords_from_name(name),
                            relaunch_when_tray_hidden=True,
                            shell_fallback_on_fail=True,
                            process_name=process_name,
                        )
                except (OSError, PermissionError) as e:
                    # 跳过无法访问的文件
                    logger.debug(f"无法访问快捷方式 {shortcut}: {e}")
                    continue
        except Exception as e:
            logger.warning(f"搜索 Start Menu 时出错 {base_dir}: {e}")
            continue

    return None


def _windows_common_paths_search(query: str) -> Optional[AppInfo]:
    """搜索常见安装路径"""
    query_lower = query.lower()
    query_normalized = query_lower.replace(" ", "").replace("-", "")

    # 常见安装目录
    common_dirs = [
        Path(r"C:\Program Files"),
        Path(r"C:\Program Files (x86)"),
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs",
        Path(os.environ.get("APPDATA", "")),
    ]

    # 常见应用目录名映射（支持多种别名）
    app_dir_map = {
        "微信": ["Tencent/WeChat", "WeChat"],
        "wechat": ["Tencent/WeChat", "WeChat"],
        "weixin": ["Tencent/WeChat", "WeChat"],
        "qq": ["Tencent/QQ/Bin", "Tencent/QQ"],
        "chrome": ["Google/Chrome/Application"],
        "googlechrome": ["Google/Chrome/Application"],
        "edge": ["Microsoft/Edge/Application"],
        "microsoftedge": ["Microsoft/Edge/Application"],
        "vscode": ["Microsoft VS Code"],
        "code": ["Microsoft VS Code"],
        "visualstudiocode": ["Microsoft VS Code"],
        "firefox": ["Mozilla Firefox"],
        "dingtalk": ["DingTalk", "钉钉"],
        "钉钉": ["DingTalk", "钉钉"],
        "feishu": ["Feishu", "飞书"],
        "飞书": ["Feishu", "飞书"],
    }

    # 尝试直接匹配（支持去空格匹配）
    possible_subdirs = (
        app_dir_map.get(query_lower, [])
        or app_dir_map.get(query_normalized, [])
        or [query]
    )

    for base in common_dirs:
        if not base.exists():
            continue

        for subdir in possible_subdirs:
            search_path = base / subdir

            if search_path.exists():
                # 查找 .exe 文件（限制搜索深度，提升性能）
                exe_files = _find_exe_files_limited(search_path, max_depth=2)

                # 优先返回与应用名匹配的 .exe
                best_match = _select_best_exe(exe_files, query)

                if best_match:
                    logger.info(f"在常见路径找到: {best_match}")
                    return AppInfo(
                        name=query,
                        path=str(best_match),
                        keywords=[query_lower],
                        relaunch_when_tray_hidden=True,
                        shell_fallback_on_fail=True,
                        process_name=best_match.name,
                    )

    return None


def _find_exe_files_limited(search_path: Path, max_depth: int = 2) -> List[Path]:
    """限制深度查找 .exe 文件（避免递归太深）"""
    exe_files: List[Path] = []

    # 黑名单关键词
    SKIP_KEYWORDS = ["uninstall", "update", "crash", "reporter", "feedback", "helper"]

    def search_recursive(path: Path, current_depth: int) -> None:
        if current_depth > max_depth:
            return

        try:
            for item in path.iterdir():
                if item.is_file() and item.suffix.lower() == ".exe":
                    # 排除黑名单文件
                    if not any(skip in item.name.lower() for skip in SKIP_KEYWORDS):
                        exe_files.append(item)
                elif item.is_dir() and current_depth < max_depth:
                    # 递归搜索子目录
                    search_recursive(item, current_depth + 1)
        except PermissionError:
            pass
        except Exception as e:
            logger.debug(f"搜索目录时出错 {path}: {e}")

    search_recursive(search_path, 0)
    return exe_files


def _select_best_exe(exe_files: List[Path], query: str) -> Optional[Path]:
    """从多个 .exe 文件中选择最佳匹配"""
    if not exe_files:
        return None

    query_lower = query.lower().replace(" ", "").replace("-", "")

    # 评分系统
    scored_files: List[tuple[Path, int]] = []

    for exe_file in exe_files:
        score = 0
        name_lower = exe_file.stem.lower().replace(" ", "").replace("-", "")

        # 精确匹配（最高优先级）
        if name_lower == query_lower:
            score = 100
        # 包含查询词
        elif query_lower in name_lower:
            score = 70
        # 查询词包含在文件名中
        elif name_lower in query_lower:
            score = 50
        # 默认分数
        else:
            score = 10

        # 主程序通常名字较短
        if len(exe_file.stem) < 15:
            score += 5

        # 位于根目录的文件优先级更高
        depth = len(exe_file.relative_to(exe_file.parents[2]).parts) if len(exe_file.parents) > 2 else 0
        score -= depth * 5

        scored_files.append((exe_file, score))

    # 按分数排序，返回最高分
    scored_files.sort(key=lambda x: x[1], reverse=True)
    return scored_files[0][0] if scored_files[0][1] > 0 else None


def _search_macos_app_dynamic(app_name: str) -> Optional[AppInfo]:
    """macOS 平台动态搜索应用"""
    query = app_name.strip()

    # 策略1: 使用 mdfind (Spotlight) 搜索
    logger.debug(f"策略1: 使用 mdfind 搜索 '{query}'")
    try:
        result = subprocess.run(
            ["mdfind", f"kMDItemKind == 'Application' && kMDItemFSName == '*{query}*.app'"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")

            # 找到最匹配的应用
            for line in lines:
                app_path = line.strip()
                if app_path and Path(app_path).exists():
                    app_stem = Path(app_path).stem

                    # 检查是否匹配
                    if query.lower() in app_stem.lower():
                        logger.info(f"通过 mdfind 找到: {app_path}")
                        return AppInfo(
                            name=app_stem,
                            path=app_path,
                            keywords=_keywords_from_name(app_stem),
                        )
    except subprocess.TimeoutExpired:
        logger.warning(f"mdfind 命令超时: {query}")
    except Exception as e:
        logger.debug(f"mdfind 命令失败: {e}")

    # 策略2: 尝试 open -a 命令（让系统查找）
    logger.debug(f"策略2: 使用 open -a 测试 '{query}'")
    # 注意：这里不实际执行 open，只是返回一个特殊的 AppInfo
    # 让 activator 使用 open -a 启动
    return AppInfo(
        name=query,
        path=f"open://{query}",  # 特殊标记
        keywords=[query.lower()],
    )


def _search_linux_app_dynamic(app_name: str) -> Optional[AppInfo]:
    """Linux 平台动态搜索应用"""
    query = app_name.strip()

    # 策略1: 使用 which 命令
    logger.debug(f"策略1: 使用 which 命令查找 '{query}'")
    try:
        result = subprocess.run(
            ["which", query],
            capture_output=True,
            text=True,
            timeout=3
        )

        if result.returncode == 0 and result.stdout.strip():
            app_path = result.stdout.strip()

            if app_path and Path(app_path).exists():
                logger.info(f"通过 which 命令找到: {app_path}")
                return AppInfo(
                    name=query,
                    path=app_path,
                    keywords=[query.lower()],
                )
    except subprocess.TimeoutExpired:
        logger.warning(f"which 命令超时: {query}")
    except Exception as e:
        logger.debug(f"which 命令失败: {e}")

    # 策略2: 搜索 .desktop 文件
    logger.debug(f"策略2: 搜索 .desktop 文件")
    desktop_dirs = [
        Path("/usr/share/applications"),
        Path.home() / ".local/share/applications",
    ]

    for desktop_dir in desktop_dirs:
        if not desktop_dir.exists():
            continue

        for desktop_file in desktop_dir.glob("*.desktop"):
            if query.lower() in desktop_file.stem.lower():
                # 解析 .desktop 文件获取 Exec 路径
                try:
                    content = desktop_file.read_text(encoding="utf-8")
                    for line in content.split("\n"):
                        if line.startswith("Exec="):
                            exec_line = line[5:].strip()
                            # 提取可执行文件路径（去除参数）
                            exec_path = exec_line.split()[0]

                            logger.info(f"通过 .desktop 文件找到: {exec_path}")
                            return AppInfo(
                                name=desktop_file.stem,
                                path=exec_path,
                                keywords=[query.lower()],
                            )
                except Exception as e:
                    logger.debug(f"解析 .desktop 文件失败: {e}")
                    continue

    logger.warning(f"Linux 平台未找到应用: {app_name}")
    return None
