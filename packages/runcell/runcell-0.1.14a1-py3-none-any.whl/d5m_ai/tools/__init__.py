"""
D5M AI Tools Package

This package contains standalone tools that can be used by agents or other systems
without requiring the agent SDK.

Note: Tool specifications are defined in the remote backend server.
These tools are only for local execution by the proxy handler.
"""

from .read_file import execute_read_file_tool
from .list_dir import execute_list_dir_tool
from .grep import execute_grep_tool

__all__ = [
    'execute_read_file_tool',
    'execute_list_dir_tool',
    'execute_grep_tool'
] 