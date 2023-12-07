def switch_xz(x, y, z):
    return z, y, x

def shift_y(offset, x, y, z):
    return x, [yy - offset for yy in y], z
