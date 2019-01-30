from hitchbuild.monitor import Monitor
from hitchbuild import exceptions
from hitchbuild.utils import hash_json_struct
from path import Path
from copy import copy
import uuid


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


class DependencyChange(object):
    def __init__(self, dependency_changed):
        self._changed = dependency_changed

    def changes(self):
        return []

    def __len__(self):
        return len(self.changes())

    def __getitem__(self, index):
        return self.changes()[index]


class Source(Watcher):
    def __init__(self, build, name, paths):
        self._build = build
        self._name = name
        self._paths = paths
        self._build._add_watcher(self)

    def prebuild(self, monitor):
        new_files = list(self._paths)
        modified_files = []

        from os import path as ospath

        for monitored_file in monitor.File.filter(build=monitor.build_model)\
                                          .filter(name=self._name):
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
                name=self._name,
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
                if hash_json_struct(self._variables[name]) != var.hashval:
                    modified_vars.append(name)
                    var.hashval = hash_json_struct(self._variables[name])
                    var.strval = str(self._variables[name])
                    var.save()

        for name in new_vars:
            var_model = monitor.Variable(
                build=monitor.build_model,
                name=name,
                hashval=hash_json_struct(self._variables[name]),
                strval=str(self._variables[name]),
            )
            var_model.save()

        self.changes = VarChanges(list(new_vars.keys()), modified_vars)


#class Dependency(object):
    #def __init__(self, parent, child):
        #self._parent = parent
        #self._child = child

    #@property
    #def build(self):
        #return self._child

    #def name(self):
        #return self._child.name

    #def ensure_built(self):
        #self.build.ensure_built()

    #def rebuilt(self):
        #return self._parent.monitor.rebuilt(self._child).check()



class Dependency(object):
    def __init__(self, parent, child):
        self._parent = parent
        self._child = child

    @property
    def build(self):
        return self._parent

    def trigger(self):
        expected_fingerprint = self._child.fingerprint.deps.get(self._parent.name)
        actual_fingerprint = self._parent.fingerprint.get()
        if expected_fingerprint is None or actual_fingerprint is None:
            return True
        return expected_fingerprint != actual_fingerprint



class HitchBuild(object):
    def __init__(self):
        pass

    def from_source(self, name, paths):
        return Source(self, name, paths)

    def monitored_vars(self, **variables):
        return MonitoredVars(self, variables)

    def build(self):
        raise NotImplementedError("build method must be implemented")

    @property
    def fingerprint(self):
        assert hasattr(self, 'fingerprint_path'),\
            "fingerprint_path on object should be set"

        import json
        import random

        class Fingerprint(object):
            def __init__(self, build):
                self._build = build

            def file_json(self):
                return json.loads(Path(self._build.fingerprint_path).text())

            def exists(self):
                return self._build.fingerprint_path.exists()

            def get(self):
                return self.file_json()['fingerprint'] if self.exists() else None

            @property
            def deps(self):
                return self.file_json()['deps'] if self.exists() else {}

            def new(self):
                deps = {}

                if hasattr(self._build, '_triggers'):
                    for trigger, _ in self._build._triggers:
                        if isinstance(trigger, Dependency):
                            deps[trigger._parent.name] = trigger._parent.fingerprint.get()

                if not self.exists():
                    self._build.fingerprint_path.write_text(
                        json.dumps({
                            "fingerprint": str(uuid.uuid1()),
                            "deps": deps,
                        })
                    )
                else:
                    new_json = self.file_json()
                    new_json['fingerprint'] = str(uuid.uuid1())
                    new_json['deps'] = deps
                    self._build.fingerprint_path.write_text(json.dumps(new_json))

        return Fingerprint(self)

    def nonexistent(self, path):
        class NonExistent(object):
            def __init__(self, path):
                self._path = path

            def trigger(self):
                return not self._path.exists()

        return NonExistent(path)


    def dependency(self, build):
        return Dependency(build, self)

    def trigger(self, trigger_object):
        if not hasattr(self, '_triggers'):
            self._triggers = []
        self._triggers.append((trigger_object, self.build))

    @property
    def last_run_had_exception(self):
        return self.monitor.last_run_had_exception

    @property
    def monitor(self):
        return Monitor(self.name, self.build_database)

    def with_name(self, name):
        new_build = copy(self)
        new_build._name = name
        return new_build

    #@property
    #def build_path(self):
        #if hasattr(self, '_build_path'):
            #return self._build_path
        #elif hasattr(self, '_defaults_from'):
            #return self._defaults_from.build_path
        #else:
            #raise Exception("No build path set")

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

    def as_dependency(self, build):
        return Dependency(self, build)

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
        class BuildContextManager(object):
            def __init__(self, build):
                self._build = build

            def __enter__(self):
                pass

            def __exit__(self, type, value, traceback):
                if value is None:
                    self._build.fingerprint.new()

        if hasattr(self, '_triggers'):
            methods = []
            for trigger, method in self._triggers:
                if trigger.trigger():
                    if method not in methods:
                        methods.append(method)
            for method in methods:
                with BuildContextManager(self):
                    method()

    def generate_new_fingerprint(self):
        """
        Let dependent builds know that this build has changed
        and that they might need to rebuild.
        """
        model = self.monitor.build_model
        model.fingerprint = str(uuid.uuid1())
        model.save()

    def __repr__(self):
        return """HitchBuild("{0}")""".format(self.name)
