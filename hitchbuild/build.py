import copy


class HitchBuild(object):
    _built_if_exists = False
    _requirements = {}
    #_path = None

    def exists(self):
        raise NotImplemented()

    def build(self):
        raise NotImplemented()

    @property
    def path(self):
        return self._path

    def in_path(self, path):
        new_build = copy.copy(self)
        new_build._path = path
        return new_build

    def ensure_built(self):
        if self._built_if_exists:
            if self.exists():
                return
        for name, requirement in self._requirements.items():
            requirement.in_path(self.path).ensure_built()
        self.build()

    def requirement(self, **requirements):
        new_build = copy.copy(self)
        new_build._requirements = requirements
        return new_build
