def lerp(start, end, percent):
    return start + (end - start) * percent


def mod(x, y):
    r = x % y
    if x < 0:
        return -r
    return r


def fast_square(x):
    if not x:
        return x
    a = 2
    n = 1
    c = 0
    r = 100
    while c < r:
        m = n - (((n ** a) - x) / (a * x))
        n = m
        c += 1
    return n
