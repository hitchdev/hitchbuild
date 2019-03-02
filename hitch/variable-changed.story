Variable changed:
  based on: HitchBuild
  description: |
    Using HitchBuild you can feed an arbitrary variable into the
    build system and use it to determine whether or not to rebuild.

    Some examples:

    - Building python virtualenv with a list of packages (variable).
    - A version for the build itself (trigger a rebuild if the code has changed).

    HitchBuild will hash any variable it is passed to determine if it
    has changed. Any of the following types or a combination can be used -

    * Dict
    * List
    * String
    * Float
    * Integer
    * Boolean
  given:
    files:
      sourcefile.txt: |
        the contents of this file, if changed, will trigger a rebuild.
    setup: |
      from path import Path
      import hitchbuild

      class Virtualenv(hitchbuild.HitchBuild):
          def __init__(self, src_dir, build_dir, extra_packages):
              self._src_dir = Path(src_dir)
              self._build_dir = Path(build_dir).abspath()
              self._extra_packages = extra_packages
              self.fingerprint_path = self._build_dir / "fingerprint.txt"
              self.trigger(self.nonexistent(self.fingerprint_path))
              self.trigger(
                  self.vars_changed(extra_packages=extra_packages),
                  self.pipinstall
              )

          def log(self, message):
              self._build_dir.joinpath("..", "log.txt").write_text(message + '\n', append=True)

          @property
          def thingpath(self):
              return self._build_dir / "thing.txt"

          def pipinstall(self):
              for package in self._extra_packages:
                  self.log("pip install {}".format(package))

          def build(self):
              self.clean()
              self._build_dir.mkdir()
              self.thingpath.write_text("create virtualenv", append=True)

          def clean(self):
              if self._build_dir.exists():
                  self._build_dir.rmtree()

  steps:
  - Run code: |
      Virtualenv("src", "build", ["ipython", "ipdb", ]).ensure_built()
      Virtualenv("src", "build", ["ipython", "ipdb", ]).ensure_built()

  - File contents will be:
      filename: log.txt
      text: |
        pip install ipython
        pip install ipdb

  - Run code: |
      Virtualenv("src", "build", ["ipython", "ipdb", "q",]).ensure_built()

  - File contents will be:
      filename: log.txt
      text: |
        pip install ipython
        pip install ipdb
        pip install ipython
        pip install ipdb
        pip install q

  - Run code: |
      Virtualenv("src", "build", ["ipython", "ipdb", "q",]).ensure_built()

  - File contents will be:
      filename: log.txt
      text: |
        pip install ipython
        pip install ipdb
        pip install ipython
        pip install ipdb
        pip install q
