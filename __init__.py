#! python3
"""Nautilus package
"""
from mwx.framework import App
from mwx.graphman import Layer, Thread
from .wxNautilus import MainFrame as Frame


def deb(target=None, loop=True, **kwargs):
    import mwx
    from .debut import main
    with App(loop):
        frame = mwx.deb(target, loop=0, **kwargs) # Don't enter loop.
        main(frame)
        return frame
