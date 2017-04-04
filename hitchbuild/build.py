import copy


class HitchBuild(object):
    _built_if_exists = False
    _requirements = {}

    def exists(self):
        raise NotImplemented()

    def ensure_built(self, path):
        self.path = path
        if self._built_if_exists:
            if self.exists():
                return
        for name, requirement in self._requirements.items():
            requirement.ensure_built(path)
        self.build()

    def requirement(self, **requirements):
        new_build = copy.copy(self)
        new_build._requirements = requirements
        return new_build
