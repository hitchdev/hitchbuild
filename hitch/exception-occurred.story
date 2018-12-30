Exception occurred during build:
  based on: HitchBuild
  description: |
    If an exception occurs during a build, it is presumed that
    it needs to be run again, no matter what.
  given:
    files:
      sourcefile.txt: |
        file that, if changed, should trigger a rebuild
    setup: |
      from path import Path
      import hitchbuild

      class Thing(hitchbuild.HitchBuild):
          def __init__(self, build_path):
              self._build_path = Path(build_path).abspath()
              self.build_database = self._build_path / "builddb.sqlite"

          @property
          def thingpath(self):
              return self.build_path / "thing.txt"

          def build(self):
              self.thingpath.write_text(
                  "last run had exception: {}\n".format(self.last_run_had_exception),
                  append=True
              )
              self.thingpath.write_text("oneline\n", append=True)

              raise Exception("build had an error")
  steps:
  - Run code:
      code: |
        Thing(".").ensure_built()
      raises:
        type: builtins.Exception
        message: build had an error

  - File contents will be:
      filename: thing.txt
      text: |
        last run had exception: False
        oneline

  - Run code:
      code: |
        Thing(".").ensure_built()
      raises:
        type: builtins.Exception
        message: build had an error

  - File contents will be:
      filename: thing.txt
      text: |
        last run had exception: False
        oneline
        last run had exception: True
        oneline
