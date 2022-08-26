#! python3
# -*- coding: utf-8 -*-
"""Gumowski-Mira Map - Mythic Bird

http://www.atomosyd.net/spip.php?article98
"""
import wx
import numpy as np
from matplotlib import pyplot as plt
from mwx.controls import Button, LParam
from mwx.graphman import Layer


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
        self.alpha = LParam("alpha", (0, 0.1, 5e-4), 0.01, updater=self.run)
        self.sigma = LParam("sigma", (0, 0.1, 5e-4), 0.05, updater=self.run)
        self.mu = LParam("mu", (-1.0, 1.01, 0.001), -0.8, updater=self.run)
        self.layout((
                self.alpha,
                self.sigma,
                self.mu,
            ),
            title='parameters',
            style='button', type=None, lw=42, tw=42,
        )
        self.layout((
                Button(self, "Run", handler=self.run, icon='->'),
                Button(self, "Clear", handler=self.clear, icon='trash'),
                Button(self, "Output", handler=self.output_hist, icon='load'),
            ),
            row=2,
        )
        self.clear(0)
    
    def clear(self, evt):
        self.xy = 1., 1.
        self.XY = np.resize(0., (2,0))
        axes = self.graph.axes
        ## axes.grid(True)
        self.Arts = axes.plot([], [], 'ro', lw=0.5, ms=0.5, zorder=2,
                              picker=True, pickradius=4)
        self.graph.load(np.resize(0, (1024,1024)), "*background*", localunit=0.05)
    
    def calc(self, N):
        data = []
        x, y = self.xy
        for j in range(N):
            x, y = F(x, y, self.alpha.value, self.sigma.value, self.mu.value)
            data.append((x, y))
        data = np.array(data).T
        self.xy = x, y # update the last x, y
        self.XY = np.hstack((self.XY, data)) # stack new data
        return data
    
    def run(self, evt):
        self.message("calculating...")
        data = self.calc(N=100000)
        art = self.Arts[0]
        ## art.set_data(*self.XY)
        art.set_data(*data)
        self.message("\b drawing to graph...")
        self.graph.draw(art)
        self.message("\b done. Total {:,} points".format(self.XY.shape[1]))
    
    def output_hist(self, evt):
        h, x, y, mesh = plt.hist2d(*self.XY, bins=1024)
        self.output.load(np.int16(h), "*histogram*", localunit=1)
        self.output.draw()


if __name__ == "__main__":
    from mwx.graphman import Frame
    
    app = wx.App()
    frm = Frame(None)
    frm.load_plug(Plugin, show=1, dock=4)
    frm.Show()
    app.MainLoop()
