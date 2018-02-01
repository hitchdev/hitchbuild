class HitchBuildException(Exception):
    pass


class BuildPathNonexistent(HitchBuildException):
    def __init__(self, path):
        super(HitchBuildException, self).__init__(
            "Cannot build. Build path '{0}' nonexistent.".format(path)
        )
