import copy


class HitchBuild(object):
    def __init__(self):
        self._requirements = {}

    def ensure_built(self, path):
        self.path = path
        for name, requirement in self._requirements.items():
            requirement.ensure_built(path)
        self.build()

    def requirement(self, **requirements):
        new_build = copy.copy(self)
        new_build._requirements = requirements
        return new_build
