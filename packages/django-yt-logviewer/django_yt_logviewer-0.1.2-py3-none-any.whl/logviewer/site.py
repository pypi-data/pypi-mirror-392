import os
import re
from pathlib import Path

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

SYSTEM_APP_LABEL = "system"
ANSI_PATTERN = re.compile(r"\x1b\[([0-9;]*)m")
FOREGROUND_COLORS = {
    "30": "#000000",
    "31": "#cc0000",
    "32": "#00a000",
    "33": "#c8a000",
    "34": "#0000cc",
    "35": "#a000a0",
    "36": "#008c8c",
    "37": "#cccccc",
    "90": "#555555",
    "91": "#ff5555",
    "92": "#55ff55",
    "93": "#ffff55",
    "94": "#5588ff",
    "95": "#ff55ff",
    "96": "#55ffff",
    "97": "#ffffff",
}
BACKGROUND_COLORS = {
    "40": "#000000",
    "41": "#cc0000",
    "42": "#00a000",
    "43": "#c8a000",
    "44": "#0000cc",
    "45": "#a000a0",
    "46": "#008c8c",
    "47": "#cccccc",
    "100": "#555555",
    "101": "#ff5555",
    "102": "#55ff55",
    "103": "#ffff55",
    "104": "#5588ff",
    "105": "#ff55ff",
    "106": "#55ffff",
    "107": "#ffffff",
}
LOG_LEVEL_CSS_CLASSES = {
    "DEBUG": "log-level-debug",
    "INFO": "log-level-info",
    "WARNING": "log-level-warning",
    "WARN": "log-level-warning",
    "ERROR": "log-level-error",
    "CRITICAL": "log-level-critical",
    "FATAL": "log-level-critical",
}
LOG_LEVEL_PATTERN = re.compile(
    r"\b(" + "|".join(LOG_LEVEL_CSS_CLASSES.keys()) + r")\b", re.IGNORECASE
)


def _get_log_dir() -> Path:
    candidate = getattr(
        settings,
        "LOG_VIEWER_LOG_DIR",
        getattr(
            settings,
            "ADMIN_LOG_VIEWER_LOG_DIR",
            getattr(settings, "LOG_DIR", Path(settings.BASE_DIR) / "data" / "logs"),
        ),
    )
    return Path(candidate)


def _available_log_files(log_dir: Path):
    if not log_dir.exists():
        return []
    return sorted(
        [path.name for path in log_dir.glob("*.log") if path.is_file()],
        reverse=True,
    )


def _read_log_contents(log_path: Path):
    if not log_path.exists():
        return ""

    data = log_path.read_bytes()

    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="ignore")


def _build_style(color, background, bold):
    parts = []
    if color:
        parts.append(f"color: {color};")
    if background:
        parts.append(f"background-color: {background};")
    if bold:
        parts.append("font-weight: bold;")
    return " ".join(parts)


def _highlight_log_levels_html(text: str) -> str:
    if not text:
        return text

    def repl(match: re.Match) -> str:
        matched_text = match.group(0)
        css_class = LOG_LEVEL_CSS_CLASSES.get(matched_text.upper())
        if not css_class:
            return matched_text
        return f'<span class="{css_class}">{matched_text}</span>'

    return LOG_LEVEL_PATTERN.sub(repl, text)


def _ansi_to_html(log_text: str):
    if not log_text:
        return mark_safe("")

    result = []
    last_end = 0
    current_color = None
    current_bg = None
    current_bold = False

    def append_text(segment):
        if not segment:
            return
        escaped = escape(segment)
        highlighted = _highlight_log_levels_html(escaped)
        style = _build_style(current_color, current_bg, current_bold)
        if style:
            result.append(f'<span style="{style}">{highlighted}</span>')
        else:
            result.append(highlighted)

    for match in ANSI_PATTERN.finditer(log_text):
        append_text(log_text[last_end : match.start()])
        codes = match.group(1)
        if codes == "":
            codes_list = ["0"]
        else:
            codes_list = [code for code in codes.split(";") if code]
        for code in codes_list:
            if code == "0":
                current_color = None
                current_bg = None
                current_bold = False
            elif code == "1":
                current_bold = True
            elif code == "22":
                current_bold = False
            elif code == "39":
                current_color = None
            elif code == "49":
                current_bg = None
            elif code in FOREGROUND_COLORS:
                current_color = FOREGROUND_COLORS[code]
            elif code in BACKGROUND_COLORS:
                current_bg = BACKGROUND_COLORS[code]
            # Ignore unsupported codes silently
        last_end = match.end()

    append_text(log_text[last_end:])
    return mark_safe("".join(result))


def _format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    units = ["KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    unit = "B"
    for unit in units:
        size /= 1024.0
        if size < 1024.0:
            break
    return f"{size:.1f} {unit}"


def _system_module(request, log_url):
    return {
        "name": _("System"),
        "app_label": SYSTEM_APP_LABEL,
        "app_url": log_url,
        "has_module_perms": True,
        "models": [
            {
                "name": _("Log files"),
                "object_name": "LogFiles",
                "admin_url": log_url,
                "view_only": True,
                "perms": {"change": True},
                "add_url": None,
            }
        ],
    }


def _merge_system_module(apps_list, system_module):
    updated_apps = []
    replaced = False
    for app in apps_list:
        if app.get("app_label") == SYSTEM_APP_LABEL:
            updated_apps.append(system_module)
            replaced = True
        else:
            updated_apps.append(app)

    if not replaced:
        updated_apps.append(system_module)

    return updated_apps


def _remove_system_module(apps_list):
    return [app for app in apps_list if app.get("app_label") != SYSTEM_APP_LABEL]


def _should_include_module(request):
    resolver_match = getattr(request, "resolver_match", None)
    if resolver_match:
        if resolver_match.view_name == "admin:app_list":
            return False
        if resolver_match.view_name in {"admin:index", "admin:system-logs"}:
            return True
        return True

    path = getattr(request, "path", "").strip("/")
    segments = [segment for segment in path.split("/") if segment]
    if not segments:
        return True
    if segments == ["admin"]:
        return True
    if len(segments) == 2 and segments[0] == "admin":
        return False
    return True


def _inject_system_module(context, request, log_url):
    available_apps = list(context.get("available_apps", []))
    system_module = _system_module(request, log_url)
    if _should_include_module(request):
        updated_apps = _merge_system_module(available_apps, system_module)
    else:
        updated_apps = _remove_system_module(available_apps)
    context["available_apps"] = updated_apps
    context["app_list"] = updated_apps
    return context


def _log_file_view(request, site):
    log_dir = _get_log_dir()
    log_files = _available_log_files(log_dir)
    selected_file = request.GET.get("filename")
    if selected_file not in log_files:
        selected_file = log_files[0] if log_files else None

    if request.GET.get("download") == "1" and selected_file:
        file_path = log_dir / selected_file
        if file_path.exists():
            response = HttpResponse(
                file_path.read_bytes(), content_type="text/plain; charset=utf-8"
            )
            response["Content-Disposition"] = (
                f'attachment; filename="{os.path.basename(selected_file)}"'
            )
            return response

    log_content = ""
    if selected_file:
        selected_path = log_dir / selected_file
        log_content = _read_log_contents(selected_path)
        log_file_size = selected_path.stat().st_size if selected_path.exists() else 0
    else:
        log_file_size = 0
    log_content_html = _ansi_to_html(log_content)
    formatted_file_size = _format_file_size(log_file_size)

    context = {
        **site.each_context(request),
        "title": _("Log files"),
        "log_files": log_files,
        "selected_log_file": selected_file,
        "log_content": log_content,
        "log_content_html": log_content_html,
        "log_file_size": log_file_size,
        "formatted_log_file_size": formatted_file_size,
        "log_dir_exists": log_dir.exists(),
        "log_dir": log_dir,
    }
    return render(request, "logviewer.html", context)


def patch_admin_site(site=None):
    site = site or admin.site

    if getattr(site, "_logviewer_patched", False):
        return site

    original_get_urls = site.get_urls

    def get_urls():
        log_urlpattern = [
            path(
                "system/logs/",
                site.admin_view(lambda request: _log_file_view(request, site)),
                name="system-logs",
            )
        ]
        return log_urlpattern + original_get_urls()

    site.get_urls = get_urls

    original_each_context = site.each_context
    original_get_app_list = site.get_app_list

    def each_context(request):
        context = original_each_context(request)
        log_url = reverse("admin:system-logs")
        return _inject_system_module(context, request, log_url)

    site.each_context = each_context

    def get_app_list(request, app_label=None):
        app_list = list(original_get_app_list(request, app_label))
        log_url = reverse("admin:system-logs")
        system_module = _system_module(request, log_url)
        if _should_include_module(request):
            return _merge_system_module(app_list, system_module)
        return _remove_system_module(app_list)

    site.get_app_list = get_app_list

    site._logviewer_patched = True
    return site


patch_admin_site()
