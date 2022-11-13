#! python3
# -*- coding: utf-8 -*-
"""Nautilus package
"""
from mwx.graphman import Layer
from .wxNautilus import MainFrame as Frame


def deb(target=None, loop=True, **kwargs):
    import wx
    import mwx
    from .debut import main
    if loop:
        app = wx.GetApp() or wx.App()
    frame = mwx.deb(target=None, loop=0, **kwargs) # Don't enter loop.
    frame.Show()
    main(frame)
    if loop and not app.GetMainLoop():
        app.MainLoop()
    return frame
