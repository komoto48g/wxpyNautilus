#! python3
# -*- coding: utf-8 -*-
"""Nautilus package
"""
import contextlib

from mwx.graphman import Layer
from .wxNautilus import MainFrame as Frame


@contextlib.contextmanager
def app(loop=True):
    import wx
    app = wx.GetApp() or wx.App()
    yield app
    if loop and not app.GetMainLoop():
        app.MainLoop()


def deb(target=None, loop=True, **kwargs):
    import mwx
    from .debut import main
    with app(loop):
        frame = mwx.deb(target, loop=0, **kwargs) # Don't enter loop.
        main(frame)
        return frame
