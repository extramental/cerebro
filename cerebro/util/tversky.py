def make_bigrams(xs):
    """
    Make a list of bigrams from a list (or string).

    e.g.

        night -> ni ig gh ht
    """
    return zip(xs, xs[1:])


def tversky(x, y, alpha=0.5, beta=0.5):
    """
    Compute the Tversky index between sets x and y with the parameters alpha
    and beta.

    This is used to check which paragraph is most suitable to attach orphaned
    comments to.

    By default, 0.5 is used for both alpha and beta, resulting in Dice's
    coefficient. A good[citation needed] threshold is 75%.
    """
    x = set(x)
    y = set(y)

    len_x_y = len(x & y)

    return len_x_y / float(len_x_y + alpha * len(x - y) + beta * len(y - x))
