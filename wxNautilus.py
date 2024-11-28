#! python3
"""The frontend of Graph and Plug manager
"""
__version__ = "1.1rc"
__author__ = "Kazuya O'moto <komoto@jeol.co.jp>"
__copyright__ = "Copyright (c) 2018-2024"
__license__ = """\
This program is under MIT license
see https://opensource.org/licenses/MIT

logo icon: Submarine icons created by Smashicons - Flaticon
see https://www.flaticon.com/free-icons/submarine
"""
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
        
        HOME = os.path.dirname(__file__)
        for f in [
                HOME,   # Add ~/ to import si:home
                '',     # Add ./ to import si:local first
                ]:
            if f not in sys.path:
                sys.path.insert(0, f)
        try:
            si = __import__('siteinit')
        except ImportError:
            print("- No siteinit file.")
        else:
            print(f"Executing {si.__file__!r}")
            si.init_mainframe(self)
        try:
            import debut
            debut.stylus(self.shellframe)
        except ImportError:
            pass


submarine = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlw'
    b'SFlzAAAA7AAAAOwBeShxvQAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoA'
    b'AAWHSURBVFiFxZd7bBRVFMZ/dx67O9snu3QppYVWoIrxARZBhCAoRRIfoCkGozUpBq0RE9EI'
    b'RkWDhJeiBsQHvtAEioJVIWoMAhE1IEhB1AQCiIoCrV3oY9vuzs7j+sdK6bZNH4r6JfPH3O+e'
    b'8333zLkzd+B/hvov5BwKTAN+B1r+awPZwAHAC+wFas5z/m5xHbCvNwFKJ2N9Ae1vGhCA29sA'
    b'SJTMAOqBxcAG4LtuYgcbOk95dIJnByybvqbNRf3T2FdvsqMpxkLA6c7AUHTvXhzbj6AUx3kX'
    b'yEHRZoPbjOu+CDS2D0zzsXt6EUWj80WHPoo3Slbuwj0SphSo6MqABhSLIVd6GD5Jk5tfKKO5'
    b'oRKvf48YNTVEY60jD+++iWjkqnZx/pY4VyyZJtRQWsek5hnYfwLlSJi8rsTPGvhYHquaz+Fv'
    b'+uDYK4ECFCUoZr+uE43osixnFKADVpu4cfkBYqE0UrsT6ImB45jR/m1EvLhORL49V6O+xsWX'
    b'cpBok5UUpDDxeB2pgYdkUrLSq2DFbYLeQAOGp3mp1BSsJpNXLJeVmNExcvtbc3FlE5a5tH1Q'
    b'qo8blt0imDQsebyzx9ETA5MnXEhu+XjhKa+Qi6vriVkuqzFj97aZNwgYAPgBtTHKxekGHKtN'
    b'Tnb23orAyQgA+cDFwDEg1pkBAcybOZYFb5YK74YquG+d3HOmhdFA0KMxx+PhHtshMxTENHyJ'
    b'Pa5KVHFuC3eERBESEQf7dAN6cwtqn3S+PhVmLrCnfQVaEfCDK+kDXG94eW/SWDxz78EYMwJU'
    b'Fb2LSgICqeYgnBMg/Ei1H0jLK5xTHD/uUrFRGb9srbNTU6kI13M3fzV1hzdexCTPb7Bp3fN4'
    b'pxV3LdkWrj4CM1CJ73QxtnE7dko5UmogdEKBb3mkcIWYeetW9daH7TsVxS344wwTAKf1Vey4'
    b'sP5baYUCiN2VvRMHUKx9GDUFCPsoemQhRvUA/DX9MP4oRIutx0p7kqyheWxZpYm8LHF1IIOl'
    b'ibrBvOlFPN0QRdbYyM/ewZed1TvxXsERHKnyMHymabfEGKwAbKzC4wvBzspz4o4Di1er5E7O'
    b'JHhNHx5YYhBt08c94Z9+SSV7Ynoyr0qGDHEpmaCqPg+zSE3h87ISTOcwUh49d82ZpUv/4EIp'
    b'nvxEKrPXSeWCkbJ4ckaP+dllXfA/qPLDRR6ZE+JnoanE1zyDnt0XhgyC/FywHfBfpuEs/w5C'
    b'+eC4iL1fIl+ezq9bo2Rndc0HMyF9hIr7/IFO+dyAwuH9OkWzzJhiO+jL34BHn4W1mxLla4iA'
    b'60oI5iYGVAWMNJSUTKpre8ZL6JQ/UQMoklQDzDi64jcIv/A47P0Inrg/MT+YCQMHemHHWgBE'
    b'cwR59Bu0eAOXFHbPZ2fBgAGeTvh6LilMNOLJsCQ9lSYUhSV9MzCrNiX3wO5KZEbAJ1MuvVJq'
    b'w8ZKPcUvN60WPeZ3bkSmZnhaec3wyfdfSvDuPk0uv1+T/YNsEcC8giCLa1twK1ag3XTtuU4+'
    b'XQ9bvgIzDpPGQm528o7qjg/XwadfQMyEKeNhYA4gwa72cllp3Dn4i5zR+i2YMVJ4S16T9oKH'
    b'UB4s6/SseH7QorJqjcKCt63fwnXktwoVD4M1dwltziKU8vnE7S5Pcn8TluCzLSqPvmpZ4Tqm'
    b'Am7SStN94Pdyct1mDo0pIXrop/OnHW1QWPicSsn8eLw5ys3Afmj3MXIleBUidc2M/PEICy6/'
    b'kTnjRuLcfB0pBXng9/VO1Hagplqwq0q4H2xzpaq63zdHuQM4eHZOkoFth6TtSA4AVizGY8Bz'
    b'23dRUvUDUxSVAinx91RcVVB0DaGrsvZMo/yyOcoGEn9LHVCek0lL0SAaDZ0wcEHv1vnPIAAP'
    b'MB2IAtuAhv/SwP+OPwHQOY8lXV9GPgAAAABJRU5ErkJggg==')


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--session')
    argv = parser.parse_args()

    app = wx.App()
    frm = MainFrame(None)
    ssn = argv.session
    if ssn:
        if not ssn.endswith(".jssn"):
            ssn += ".jssn"
        try:
            print(f"Starting session {ssn!r}")
            frm.load_session(ssn, flush=False)
        except FileNotFoundError:
            print(f"- No such file {ssn!r}")
    frm.Show()
    app.MainLoop()
