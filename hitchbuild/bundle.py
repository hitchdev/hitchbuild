from hitchbuild.build import HitchBuild
from copy import copy


class BuildBundle(object):
    def __init__(self, build_path):
        self._build_path = build_path
        self._sqlite_filename = build_path.build.joinpath("builddb.sqlite")
        self._builds = {}

    def __setitem__(self, name, build):
        assert isinstance(name, str), "name must be a string"
        assert isinstance(build, HitchBuild), "must assign a build of type HitchBuild"
        self._builds[name] = build.with_name(name)\
                                  .with_db(self._sqlite_filename)\
                                  .in_path(self._build_path)

    def __getitem__(self, name):
        return self._builds[name]

    def ensure_built(self):
        build_triggered = True

        while build_triggered:
            build_triggered = False
            for build in self._builds.values():
                if build.ensure_built():
                    build_triggered = True

    def manually_trigger(self, *names):
        new_bundle = copy(self)
        for name in names:
            new_bundle[name] = new_bundle[name].manually_triggered()
        return new_bundle
