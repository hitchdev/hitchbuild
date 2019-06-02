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
              self.fingerprint_path = self._build_path / "fingerprint.txt"

          def build(self):
              if self.incomplete():
                  if self._build_path.exists():
                      self._build_path.rmtree()
                  self._build_path.mkdir()
                  self._build_path.joinpath("..", "thing.txt").write_text("building\n", append=True)
                  raise Exception("build had an error")
                  self.refingerprint()
  steps:
  - Run code:
      code: |
        Thing("thing").ensure_built()
      raises:
        type: builtins.Exception
        message: build had an error

  - File contents will be:
      filename: thing.txt
      text: |
        building

  - Run code:
      code: |
        Thing("thing").ensure_built()
      raises:
        type: builtins.Exception
        message: build had an error

  - File contents will be:
      filename: thing.txt
      text: |
        building
        building
