from hitchbuild.monitor import Monitor
from hitchbuild.condition import Always
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
            return 'x'

    def with_build_path(self, path):
        new_build = copy(self)
        new_build._build_path = Path(path)
        return new_build

    def with_db(self, sqlite_filename):
        new_build = copy(self)
        new_build._sqlite_filename = sqlite_filename
        return new_build
    
    def build_database(self):
        if hasattr(self, '_sqlite_filename'):
            return self._sqlite_filename
        else:
            return self._path/"builddb.sqlite"

    def with_name(self, name):
        new_build = copy(self)
        new_build._name = name
        return new_build

    def manually_triggered(self):
        new_build = copy(self)
        new_build._manually_triggered = True
        return new_build

    @property
    def was_manually_triggered(self):
        if hasattr(self, '_manually_triggered'):
            return self._manually_triggered
        else:
            return False

    def requirement(self, **requirements):
        new_build = copy(self)
        new_build._requirements = requirements
        return new_build

    def ensure_built(self):
        requirement_triggered = False

        #for requirement in self._requirements.values():
            #if requirement.monitor.build_model.was_triggered_on_last_run:
                #requirement_triggered = True

        #for requirement in self._requirements.values():
            #if requirement.ensure_built():
                #requirement_triggered = True

        trigger_check = self.trigger().check()

        triggered = (
            trigger_check or
            self.monitor.last_run_had_exception or
            self.was_manually_triggered or
            requirement_triggered
        )

        if triggered:
            with self.monitor.context_manager():
                self.build()

        #model = self.monitor.build_model
        #model.was_triggered_on_last_run = triggered
        #model.save()

        return triggered

    def __repr__(self):
        return """HitchBuild("{0}")""".format(self.name)
