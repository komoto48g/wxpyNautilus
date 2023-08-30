#! python3
# -*- coding: utf-8 -*-
"""The frontend of Graph and Plug manager
"""
__version__ = "1.0rc"
__author__ = "Kazuya O'moto <komoto@jeol.co.jp>"
__copyright__ = "Copyright (c) 2018-2022"
__license__ = """\
This program is under MIT license
see https://opensource.org/licenses/MIT

logo icon: Submarine icons created by Smashicons - Flaticon
see https://www.flaticon.com/free-icons/submarine
"""
import getopt
import sys
import os
import wx
import wx.adv
from wx.lib.embeddedimage import PyEmbeddedImage

from mwx.graphman import Frame


class MainFrame(Frame):
    """the Frontend of Graph and Plug manager
    """
    Name = "wxpyNautilus"
    
    def About(self):
        info = wx.adv.AboutDialogInfo()
        info.Name = self.Name
        info.Version = __version__
        info.Copyright = __copyright__ +' '+ __author__
        info.License = __license__
        info.Description = __doc__
        info.Developers = []
        info.DocWriters = []
        info.Artists = []
        info.SetWebSite("https://github.com/komoto48g")
        wx.adv.AboutBox(info)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.SetIcon(submarine.GetIcon())
        
        home = os.path.dirname(__file__)
        
        if home not in sys.path: # Add home (to import Frame)
            sys.path.insert(0, home)
        
        sys.path.insert(0, os.path.join(home, 'plugins'))
        sys.path.insert(0, '') # Add local . to import si:local first
        try:
            si = __import__('siteinit')
        except ImportError:
            print("- No siteinit file.")
        else:
            print(f"Executing {si.__file__!r}")
            si.init_mainframe(self)


submarine = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAAlw'
    b'SFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoA'
    b'AAJvSURBVDiNlZNPSJNhHMc/7/vu3eswN//MLUXJtliGosxhgSZ6sALN/iAYQacIA8Uu3rpU'
    b'YIdIqUOHKCzqIB2SohAKlbxkFpWplEttUG6mhPln6qZuezqo5LTCvpeHD9/f78vz8Px+sHWl'
    b'A+p/1EcpCbgFxG40dKunDOQBb9eb8bHkxsXgXFzCshwidiqACZiPDrC7WlAUK7MTTcRZu5n0'
    b'1fPT9wpQimy0XqiQ7ADhIFzrFHkP+tizPkAm6G9mMdCMznBMOljtRDNUAKgqTgFpHYMw4ANX'
    b'GsSo6Dc9IV8dqjaoON6MUhm8WfuI8GInkJ6RwJmaYkmzGEFVwDMJ00FUYBswtxYglWXTdbVS'
    b'Kj58QzQkpmLL2U1+ph2jpqLIIZSVKh2EIwglRvKNB5aGPMy4v4hKt5cBHcDMAhGjmdNtt0m1'
    b'mjd/QVgrQQ6PEtLKEXIywckXltr6jm63N5KjGA2cG5dRHt8hZdovcbFlBxlJc5gTBF/HVthm'
    b'6ifZ9IPv3h4a7o3gMH+gqkTWf/aIIor34vF1IyLDiKzyfUJpfCdMhYdE4GM0Bz8hco8X/uZ+'
    b'SdRVyTOyf564nl4IhSGoJSNS7CxrZuYWonkhAAv6VTZYCEVAliVFidc45cpCc+USk8gEo23P'
    b'qSke4EDeLOu51DmLVTeO91k7dSV97LfNcf+pGJPKsuk6kis5h/Qi0HgeqyT9Y6DXJODKdWW5'
    b'7XX4pA6gNBPjpSbaB0awnT1BZrYDg/qXtfF+kyN3HzI17BOXX76nVSqw07UzCUenm6Pjs/Tq'
    b'dOTvSqdAVtA2NhtjZcO0PzLo9vBk/TBZgO1buPgf9QutQu0u5lCEPQAAAABJRU5ErkJggg==')


if __name__ == "__main__":
    session = None
    opts, args = getopt.gnu_getopt(sys.argv[1:], "s:")
    for k, v in opts:
        if k == "-s":
            if not v.endswith(".jssn"):
                v += ".jssn"
            session = v
    
    app = wx.App()
    frm = MainFrame(None)
    if session:
        try:
            print(f"Starting session {session!r}")
            frm.load_session(session, flush=False)
        except FileNotFoundError:
            print(f"- No such file {session!r}")
    try:
        import debut
        debut.main(frm.shellframe)
    except ImportError:
        pass
    frm.Show()
    app.MainLoop()
