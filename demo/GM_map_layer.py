#! python3
"""Gumowski-Mira Map - Mythic Bird

http://www.atomosyd.net/spip.php?article98
"""
import wx
import numpy as np

from mwx.graphman import Layer
from mwx.controls import Button, LParam
from matplotlib import pyplot as plt


def G(x, mu):
    return mu * x + 2 * (1 - mu) * x**2 / (1 + x**2)


def F(x, y, alpha, sigma, mu):
    x_next = y + alpha * (1 - sigma * y**2) * y + G(x, mu)
    y_next = - x + G(x_next, mu)
    return (x_next, y_next)


class Plugin(Layer):
    """Draw Gumowski-Mira Map with three specified parameters
    """
    def Init(self):
        self.alpha = LParam("alpha", (0, 0.1, 5e-4), 0.01)
        self.sigma = LParam("sigma", (0, 0.1, 5e-4), 0.05)
        self.mu = LParam("mu", (-1.0, 1.01, 0.001), -0.8)
        self.layout((
                self.alpha,
                self.sigma,
                self.mu,
            ),
            title='parameters',
            style='button', type=None, lw=42, tw=42,
        )
        self.layout((
            Button(self, "Run",
                   lambda v: self.run(), icon='->'),
            Button(self, "Clear",
                   lambda v: self.clear(), icon='xr'),
            Button(self, "Output",
                   lambda v: self.output_hist(), icon='load'),
            ),
            row=2,
        )
        self.clear()
    
    def clear(self):
        self.xy = 1., 1.
        self.XY = np.resize(0., (2,0))
        axes = self.graph.axes
        ## axes.grid(True)
        self.Arts = axes.plot([], [], 'ro', lw=0.5, ms=0.5, zorder=2,
                              picker=True, pickradius=4)
        self.graph.load(np.resize(0, (1024,1024)),
                        "*background*", localunit=0.05)
    
    def run(self, N=100000):
        self.message("calculating...")
        params = (self.alpha.value,
                  self.sigma.value,
                  self.mu.value)
        x, y = self.xy
        data = []
        for j in range(N):
            x, y = F(x, y, *params)
            data.append((x, y))
        self.xy = data[-1]
        self.XY = np.hstack((self.XY, np.array(data).T))
        
        art = self.Arts[0]
        art.set_data(*self.XY)
        self.message("\b drawing to graph...")
        self.graph.draw(art)
        self.message("\b done. Total {:,} points".format(self.XY.shape[1]))
    
    def output_hist(self):
        h, x, y, mesh = plt.hist2d(*self.XY, bins=1024)
        self.output.load(np.int16(h), "*histogram*", localunit=1)
        self.output.draw()
        ## plt.show()
        plt.close()


if __name__ == "__main__":
    from mwx.graphman import Frame
    
    app = wx.App()
    frm = Frame(None)
    frm.load_plug(Plugin, show=1, dock=4)
    frm.Show()
    app.MainLoop()
