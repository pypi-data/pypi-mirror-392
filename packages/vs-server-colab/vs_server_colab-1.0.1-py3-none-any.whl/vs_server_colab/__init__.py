"""vs_server_script package

Exports:
 - VSExpose: main class to setup/start/teardown VS Code + ngrok
 - __version__: package version
"""
from .core import VSExpose

__all__ = ["VSExpose"]
__version__ = "1.0.0"
