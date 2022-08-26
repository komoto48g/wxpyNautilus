#! python3
# -*- coding: utf-8 -*-
"""Gumowski-Mira Map - Mythic Bird

http://www.atomosyd.net/spip.php?article98
"""

def G(x, mu):
    return mu * x + 2 * (1 - mu) * x**2 / (1 + x**2)


def F(x, y, alpha, sigma, mu):
    x_next = y + alpha * (1 - sigma * y**2) * y + G(x, mu)
    y_next = - x + G(x_next, mu)
    return (x_next, y_next)


def calc(N, x, y, alpha, sigma, mu):
    data = []
    for j in range(N):
        x, y = F(x, y, alpha, sigma, mu)
        data.append((x, y))
    return data


if __name__ == "__main__":
    import numpy as np
    from mwx.mgplt import Gnuplot
    
    N = 10**5
    x, y = 1., 1.
    data = calc(N, x, y, alpha=0.009, sigma=0.05, mu=-0.801)
    X, Y = np.array(data).T
    
    gp = Gnuplot(debug=1)
    gp.plot(X, Y, "pt 0 ps 0.1")
