from path import Path
from copy import copy
import uuid
import json


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


class NonExistent(object):
    def __init__(self, path):
        self._path = path

    def trigger(self):
        return not self._path.exists()


class Fingerprint(object):
    def __init__(self, build):
        self._build = build

    def file_json(self):
        return json.loads(Path(self._build.fingerprint_path).text())

    def exists(self):
        return self._build.fingerprint_path.exists()

    def get(self):
        return self.file_json()["fingerprint"] if self.exists() else None

    @property
    def deps(self):
        return self.file_json()["deps"] if self.exists() else {}

    def new(self):
        deps = {}
        sources = {}
        variables = {}

        if hasattr(self._build, "_triggers"):
            for trigger, _ in self._build._triggers:
                if isinstance(trigger, Dependency):
                    deps[trigger._parent.name] = trigger._parent.fingerprint.get()
                if isinstance(trigger, VarsChange):
                    for name, value in trigger.variables.items():
                        variables[name] = value

        if hasattr(self._build, "_sources"):
            for source in self._build._sources:
                sources[source.name] = source.timestamp()

        if not self.exists():
            self._build.fingerprint_path.write_text(
                json.dumps(
                    {
                        "fingerprint": str(uuid.uuid1()),
                        "deps": deps,
                        "sources": sources,
                        "variables": variables,
                    }
                )
            )
        else:
            new_json = self.file_json()
            new_json["fingerprint"] = str(uuid.uuid1())
            new_json["deps"] = deps
            new_json["sources"] = sources
            new_json["variables"] = variables
            self._build.fingerprint_path.write_text(json.dumps(new_json))


class FilesChanged(object):
    def __init__(self, build, paths):
        self._build = build
        self._paths = paths

    def file_json(self):
        return json.loads(Path(self._build.fingerprint_path).text())

    def trigger(self):
        return True


class Source(object):
    def __init__(self, build, name, paths):
        self._build = build
        self._name = name
        self._paths = paths

    @property
    def name(self):
        return self._name

    def changed(self):
        from os.path import getmtime

        json = (
            self._build.fingerprint.file_json()
            if self._build.fingerprint.exists()
            else {}
        )
        paths = json.get("sources", {}).get(self._name, {})

        for path in self._paths:
            if paths.get(path) != getmtime(path):
                return True
        return False

    def timestamp(self):
        from os.path import getmtime

        paths = {}
        for path in self._paths:
            paths[path] = getmtime(path)
        return paths


class VarsChange(object):
    def __init__(self, build, variables):
        self._build = build
        self.variables = variables

    def trigger(self):
        json = (
            self._build.fingerprint.file_json()
            if self._build.fingerprint.exists()
            else {}
        )
        existing_vars = json.get("variables", {})

        changed_vars = list(
            set(existing_vars.keys()).symmetric_difference(set(self.variables.keys()))
        )

        for existing_var in existing_vars.keys():
            if existing_var in self.variables.keys():
                if existing_vars[existing_var] != self.variables[existing_var]:
                    changed_vars.append(existing_var)

        return changed_vars


class HitchBuild(object):
    def __init__(self):
        pass

    def build(self):
        raise NotImplementedError("build method must be implemented")

    @property
    def fingerprint(self):
        assert hasattr(
            self, "fingerprint_path"
        ), "fingerprint_path on object should be set"
        return Fingerprint(self)

    def nonexistent(self, path):
        return NonExistent(path)

    def dependency(self, build):
        return Dependency(build, self)

    def source(self, name, *paths):
        if not hasattr(self, "_sources"):
            self._sources = []

        new_source = Source(self, name, paths)
        self._sources.append(new_source)

        return new_source

    def trigger(self, trigger_object, method=None):
        if not hasattr(self, "_triggers"):
            self._triggers = []
        self._triggers.append(
            (trigger_object, self.build if method is None else method)
        )

    def with_name(self, name):
        new_build = copy(self)
        new_build._name = name
        return new_build

    @property
    def name(self):
        if hasattr(self, "_name"):
            return self._name
        else:
            return type(self).__name__

    def as_dependency(self, build):
        return Dependency(self, build)

    def on_change(self, source):
        class FileChange(object):
            def __init__(self, build, source):
                self._build = build
                self._source = source

            def trigger(self):
                return self._source.changed()

        return FileChange(self, source)

    def vars_changed(self, **variables):
        return VarsChange(self, variables)

    def _add_watcher(self, watcher):
        if hasattr(self, "_watchers"):
            self._watchers.append(watcher)
        else:
            self._watchers = [watcher]

    @property
    def rebuilt(self):
        if hasattr(self, "_rebuilt"):
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
                if hasattr(self._build, "_sources"):
                    for source in self._build._sources:
                        source.timestamp()
                if value is None:
                    self._build.fingerprint.new()

        if hasattr(self, "_triggers"):
            methods = []
            for trigger, method in self._triggers:
                if trigger.trigger():
                    if method not in methods:
                        methods.append(method)
            for method in methods:
                with BuildContextManager(self):
                    method()

    def __repr__(self):
        return """HitchBuild("{0}")""".format(self.name)
