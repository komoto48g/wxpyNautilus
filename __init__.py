#! python3
# -*- coding: utf-8 -*-
"""Nautilus package
"""
from mwx.graphman import Layer
from .wxNautilus import MainFrame as Frame


def deb(target=None, loop=True, **kwargs):
    import mwx
    from .debut import main
    with mwx.app(loop):
        frame = mwx.deb(target, loop=0, **kwargs) # Don't enter loop.
        main(frame)
        return frame
