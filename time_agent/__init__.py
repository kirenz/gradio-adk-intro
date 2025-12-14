"""
Time Agent Package

This package contains the Time Agent implementation for both ADK web and Gradio.
"""

from .agent import root_agent, runner
from .tools import get_current_time

__all__ = ['root_agent', 'runner', 'get_current_time']
