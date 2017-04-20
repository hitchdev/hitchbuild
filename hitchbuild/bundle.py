from hitchbuild.build import HitchBuild


class BuildBundle(object):
    def __init__(self, build_path, sqlite_filename):
        self._build_path = build_path
        self._sqlite_filename = sqlite_filename
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
        for _, build in self._builds.items():
            build.ensure_built()
