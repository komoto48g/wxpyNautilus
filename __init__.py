#! python3
"""Nautilus package
"""
from mwx.graphman import Layer, Thread
from .wxNautilus import MainFrame as Frame


def deb(target=None, loop=True, **kwargs):
    import wx
    import mwx
    from .debut import main

    app = wx.GetApp() or wx.App()
    try:
        frame = mwx.deb(target, loop=0, **kwargs) # Don't enter loop.
        main(frame)
        return frame
    finally:
        if loop and not app.GetMainLoop():
            app.MainLoop()
