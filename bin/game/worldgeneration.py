import opensimplex
import random
import numpy as np


class WorldGenerator:
    def __init__(self, seed=None):
        if seed:
            self.simplex = opensimplex.opensimplex.OpenSimplex(seed)
        else:
            self.simplex = opensimplex.opensimplex.OpenSimplex(random.randint(0, 65565))

    def noise2(self, x, y):
        return self.simplex.noise2(x, y)

    def noise2array(self, x, y):
        return self.simplex.noise2array(x, y)

    def noise3(self, x, y, z):
        return self.simplex.noise3(x, y, z)

    def noise3array(self, x, y, z):
        return self.simplex.noise3array(x, y, z)

    def noise4(self, x, y, z, w):
        return self.simplex.noise4(x, y, z, w)

    def noise4array(self, x, y, z, w):
        return self.simplex.noise4array(x, y, z, w)


b_col = (127, 127, 127)


def default_col_func(result):
    c = int((result/2+1.5) * 128)
    return c//7, c, c//4


class Biome(object):
    def __init__(self, gradient=1, clamp=0, xfreq=1, yfreq=1, color_func=None):
        super(Biome, self).__init__()
        self.gradient = gradient
        self.clamp = clamp
        self.xfreq = xfreq
        self.yfreq = yfreq
        if color_func:
            self._col_func = color_func
        else:
            self._col_func = default_col_func

    def filter2d(self, simplex, x, y):
        return (simplex.noise2(x*self.xfreq, y*self.yfreq) ** self.gradient) - self.clamp

    def color_func(self, result):
        return self._col_func(result)
