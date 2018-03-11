from hitchbuild.monitor import Monitor
from hitchbuild.condition import Always
from hitchbuild import exceptions
from path import Path
from copy import copy


class Only(object):
    def __init__(self, last_run):
        self._last_run = last_run

    @property
    def path_changes(self):
        from hitchbuild.condition import FileChange
        filechange = False
        otherchange = False
        for change in self._last_run.checks._changes:
            if isinstance(change, FileChange):
                filechange = True
            if isinstance(change, bool):
                if change:
                    otherchange = True
        if self._last_run.last_run_had_exception:
            otherchange = True
        if self._last_run.dependency_trigger or self._last_run.manual_trigger:
            otherchange = True
        if not otherchange and filechange:
            return True
        if otherchange or not filechange:
            return False
        return None


class LastRun(object):
    def __init__(self, checks, last_run_had_exception, manual_trigger, dependency_trigger):
        self.checks = checks
        self.last_run_had_exception = last_run_had_exception
        self.manual_trigger = manual_trigger
        self.dependency_trigger = dependency_trigger

    @property
    def triggered(self):
        return self.checks or self.last_run_had_exception \
          or self.manual_trigger or self.dependency_trigger

    @property
    def only(self):
        return Only(self)

    @property
    def var_changes(self):
        from hitchbuild.condition import VarChange

        for change in self.checks._changes:
            if isinstance(change, VarChange):
                return VarChanges(change)
        return None

    @property
    def path_changes(self):
        from hitchbuild.condition import FileChange

        for change in self.checks._changes:
            if isinstance(change, FileChange):
                return PathChanges(change)
        return None


class Watcher(object):
    pass


class VarChanges(object):
    def __init__(self, modified, new):
        self._modified = modified
        self._new = new

    def changes(self):
        return self._modified + self._new

    def __len__(self):
        return len(self.changes())

    def __getitem__(self, index):
        return self.changes()[index]


class PathChanges(object):
    def __init__(self, modified, new):
        self._modified = modified
        self._new = new

    def changes(self):
        return self._modified + self._new

    def __len__(self):
        return len(self.changes())

    def __getitem__(self, index):
        return self.changes()[index]

    def __contains__(self, item):
        for modified in self.changes():
            if Path(item).abspath() == Path(item).abspath():
                return True
        return False


class Source(Watcher):
    def __init__(self, build, paths):
        self._build = build
        self._paths = paths
        self._build._add_watcher(self)

    def prebuild(self, monitor):
        new_files = list(self._paths)
        modified_files = []

        from os import path as ospath

        for monitored_file in monitor.File.filter(build=monitor.build_model):
            filename = monitored_file.filename
            if filename in self._paths:
                new_files.remove(filename)

                if ospath.getmtime(filename) != monitored_file.last_modified:
                    modified_files.append(filename)
                    monitored_file.last_modified = ospath.getmtime(filename)
                    monitored_file.save()

        for filename in new_files:
            file_model = monitor.File(
                build=monitor.build_model,
                filename=filename,
                last_modified=ospath.getmtime(filename),
            )
            file_model.save()

        self.changes = PathChanges(new_files, modified_files)


class MonitoredVars(Watcher):
    def __init__(self, build, variables):
        self._build = build
        self._variables = variables
        self._build._add_watcher(self)

    def prebuild(self, monitor):
        new_vars = self._variables.copy()
        modified_vars = []

        for var in monitor.Variable.filter(build=monitor.build_model):
            name = var.name
            del new_vars[name]
            if name in self._variables.keys():
                if str(hash(self._variables[name])) != var.hashval:
                    modified_vars.append(name)
                    var.hashval = hash(self._variables[name])
                    var.strval = str(self._variables[name])

        for name in new_vars:
            var_model = monitor.Variable(
                build=monitor.build_model,
                name=name,
                hashval=hash(self._variables[name]),
                strval=str(self._variables[name]),
            )
            var_model.save()

        self.changes = VarChanges(list(new_vars.keys()), modified_vars)


class HitchBuild(object):
    def __init__(self):
        pass

    def from_source(self, paths):
        return Source(self, paths)

    def monitored_vars(self, **variables):
        return MonitoredVars(self, variables)

    def build(self):
        raise NotImplementedError("build method must be implemented")

    def fingerprint(self):
        raise NotImplementedError("fingerprint method must be implemented")

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
        if hasattr(self, '_build_path'):
            return self._build_path
        elif hasattr(self, '_defaults_from'):
            return self._defaults_from.build_path
        else:
            raise Exception("No build path set")

    @property
    def name(self):
        if hasattr(self, '_name'):
            return self._name
        else:
            return type(self).__name__

    def with_build_path(self, path):
        new_build = copy(self)
        new_build._build_path = Path(path).abspath()

        if not new_build._build_path.exists():
            raise exceptions.BuildPathNonexistent(
                new_build._build_path.abspath()
            )
        return new_build

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

    def as_dependency(self, build):
        if hasattr(self, '_dependencies'):
            self._dependencies.append(build)
        else:
            self._dependencies = [build, ]
        return build

    def _add_watcher(self, watcher):
        if hasattr(self, '_watchers'):
            self._watchers.append(watcher)
        else:
            self._watchers = [watcher, ]

    @property
    def rebuilt(self):
        if hasattr(self, '_rebuilt'):
            return self._rebuilt
        else:
            return False

    def ensure_built(self):
        self._rebuilt = False

        if hasattr(self, '_dependencies'):
            for dependency in self._dependencies:
                dependency._defaults_from = self
                dependency.ensure_built()

        if hasattr(self, '_watchers'):
            for watcher in self._watchers:
                watcher.prebuild(self.monitor)

        model = self.monitor.build_model

        previous_fingerprint = model.fingerprint

        with self.monitor.context_manager():
            self.build()

        new_fingerprint = self.fingerprint()

        assert isinstance(new_fingerprint, str), \
            "{0} is not a string".format(new_fingerprint)
        assert len(new_fingerprint) < 256, \
            "{0} is too long, should be under 256 characters".format(new_fingerprint)

        self._rebuilt = new_fingerprint != previous_fingerprint
        model = self.monitor.build_model
        model.fingerprint = new_fingerprint
        model.save()

    def __repr__(self):
        return """HitchBuild("{0}")""".format(self.name)
