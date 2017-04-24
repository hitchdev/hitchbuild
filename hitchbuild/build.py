from hitchbuild.monitor import Monitor
from hitchbuild.condition import Always
from copy import copy


class HitchBuild(object):
    _built_if_exists = False
    _requirements = {}

    def __init__(self):
        self._name = None
        self._manually_triggered = False
        self._sqlite_filename = None

    def exists(self):
        raise NotImplemented()

    def build(self):
        raise NotImplementedError("build method must be implemented")

    def trigger(self):
        raise NotImplementedError("trigger method must be implemented")

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
        new_build = copy(self)
        new_build._path = path
        return new_build

    def with_db(self, sqlite_filename):
        new_build = copy(self)
        new_build._sqlite_filename = sqlite_filename
        return new_build

    def with_name(self, name):
        new_build = copy(self)
        new_build._name = name
        return new_build

    def manually_triggered(self):
        new_build = copy(self)
        new_build._manually_triggered = True
        return new_build

    def requirement(self, **requirements):
        new_build = copy(self)
        new_build._requirements = requirements
        return new_build

    def ensure_built(self):
        requirement_triggered = False

        for requirement in self._requirements.values():
            if requirement.monitor.build_model.was_triggered_on_last_run:
                requirement_triggered = True

        for requirement in self._requirements.values():
            if requirement.ensure_built():
                requirement_triggered = True

        trigger_check = self.trigger().check()

        triggered = (
            trigger_check or
            self.monitor.last_run_had_exception or
            self._manually_triggered or
            requirement_triggered
        )

        self._manually_triggered = False

        if triggered:
            with self.monitor.context_manager():
                self.build()

        model = self.monitor.build_model
        model.was_triggered_on_last_run = triggered
        model.save()

        return triggered

    def __repr__(self):
        return """HitchBuild("{0}")""".format(self._name)
