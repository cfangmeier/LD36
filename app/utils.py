from os.path import dirname, join, abspath


def asset_path(asset, asset_loc):
    path = join(dirname(dirname(abspath(__file__))), asset_loc, asset)
    return path
