"""
Reusable Django log viewer application.

The bulk of the implementation lives in ``logviewer.apps`` and related
modules. Install the app by adding ``"logviewer"`` to ``INSTALLED_APPS``.
"""

default_app_config = "logviewer.apps.LogViewerConfig"

__all__ = ["default_app_config"]
