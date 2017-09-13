from path import Path


class BuildPath(object):
    def __init__(self, **paths):
        assert "build" in paths, "build=pathname must be set at a minimum"
        for name, path in paths.items():
            assert Path(path), "must be valid path"
            setattr(self, name, Path(path).abspath())
