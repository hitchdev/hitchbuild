from hitchbuild.monitor import Monitor
from hitchbuild.condition import Always
from hitchbuild import exceptions
from path import Path
from copy import copy


class HitchBuild(object):
    def __init__(self):
        pass

    def exists(self):
        raise NotImplemented()

    def build(self):
        raise NotImplementedError("build method must be implemented")

    def trigger(self):
        return Always()

    @property
    def monitor(self):
        return Monitor(self.name, self.build_database)

    def with_name(self, name):
        new_build = copy(self)
        new_build._name = name
        return new_build

    @property
    def build_path(self):
        return self._build_path

    @property
    def name(self):
        if hasattr(self, '_name'):
            return self._name
        else:
            return type(self).__name__

    def with_build_path(self, path):
        new_build = copy(self)
        new_build._build_path = Path(path)

        if not new_build._build_path.exists():
            raise exceptions.BuildPathNonexistent(
                new_build._build_path.abspath()
            )
        return new_build

    def with_default_build_path(self, path):
        if hasattr(self, '_build_path'):
            return self
        else:
            return self.with_build_path(path)

    def with_db(self, sqlite_filename):
        new_build = copy(self)
        new_build._sqlite_filename = sqlite_filename
        return new_build

    @property
    def build_database(self):
        if hasattr(self, '_sqlite_filename'):
            return self._sqlite_filename
        else:
            return self.build_path / "builddb.sqlite"

    def triggered(self):
        new_build = copy(self)
        new_build._manually_triggered = True
        return new_build

    @property
    def was_manually_triggered(self):
        if hasattr(self, '_manually_triggered'):
            return self._manually_triggered
        else:
            return False

    def as_dependency(self, build):
        dependent_build = build
        if hasattr(self, '_dependencies'):
            self._dependencies.append(dependent_build)
        else:
            self._dependencies = [dependent_build, ]
        return dependent_build

    def ensure_built(self):
        dependency_triggered = False

        if hasattr(self, '_dependencies'):
            for dependency in self._dependencies:
                if dependency.with_default_build_path(self.build_path).ensure_built():
                    dependency_triggered = True

        trigger_check = self.trigger().check_all()

        triggered = (
            trigger_check or
            self.monitor.last_run_had_exception or
            self.was_manually_triggered or
            dependency_triggered
        )

        if triggered:
            with self.monitor.context_manager():
                self.build()

        model = self.monitor.build_model
        model.was_triggered_on_last_run = triggered
        model.save()

        return triggered

    def __repr__(self):
        return """HitchBuild("{0}")""".format(self.name)
