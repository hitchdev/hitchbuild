from path import Path


class BuildPath(object):
    def __init__(self, **paths):
        for name, path in paths.items():
            assert Path(path), "must be valid path"
            setattr(self, name, Path(path).abspath())
