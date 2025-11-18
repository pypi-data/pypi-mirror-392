"""Framework for testing Firefly Zero apps.
"""
from ._app import App
from ._cli import CLI
from ._color import Color
from ._frame import HEIGHT, WIDTH, Frame
from ._input import Input


__all__ = [
    'CLI',
    'HEIGHT',
    'WIDTH',
    'App',
    'Color',
    'Frame',
    'Input',
]
