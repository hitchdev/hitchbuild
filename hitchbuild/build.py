from hitchbuild.monitor import Monitor
from hitchbuild.condition import Always
import copy


class HitchBuild(object):
    _built_if_exists = False
    _requirements = {}
    #_path = None

    def exists(self):
        raise NotImplemented()

    def build(self):
        raise NotImplemented()

    def trigger(self):
        return Always()

    @property
    def monitor(self):
        return Monitor(self._name, self._sqlite_filename)

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

    def in_path(self, path):
        new_build = copy.copy(self)
        new_build._path = path
        return new_build

    def with_db(self, sqlite_filename):
        new_build = copy.copy(self)
        new_build._sqlite_filename = sqlite_filename
        return new_build

    def with_name(self, name):
        new_build = copy.copy(self)
        new_build._name = name
        return new_build

    def ensure_built(self):
        if self._built_if_exists:
            if self.exists():
                return
        for name, requirement in self._requirements.items():
            requirement.in_path(self.path).ensure_built()
        if self.trigger().check():
            self.build()

    def requirement(self, **requirements):
        new_build = copy.copy(self)
        new_build._requirements = requirements
        return new_build
