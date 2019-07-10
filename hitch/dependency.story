Dependency:
  about: |
    Dependencies are builds which:

    * Should be built in order for another build to run.
    * Should, when rebuilt, trigger that other build to rerun.

    This example shows a real example of virtualenv being built,
    which requires cpython (via pyenv) to be built first.
  based on: HitchBuild
  given:
    files:
      special/specialbuildpath.txt: |
        This directory is where the special builds go.
    setup: |
      from path import Path
      import hitchbuild
      import random

      class CPython(hitchbuild.HitchBuild):
          def __init__(self, build_path):
              self.build_path = Path(build_path).abspath()
              self.fingerprint_path = self.build_path / "fingerprint.txt"
              self.thingfile = self.build_path / "cpython.txt"
              self.logfile = self.build_path / ".." / "log.txt"

          def build(self):
              if self.incomplete():
                  if self.build_path.exists():
                      self.build_path.rmtree()
                  self.build_path.mkdir()
                  self.thingfile.write_text(
                      str(random.randrange(10**6, 10**7))
                  )
                  self.logfile.write_text("cpython built\n", append=True)
                  self.refingerprint()

          def clean(self):
              if self.build_path.exists():
                  self.build_path.rmtree()


      class Virtualenv(hitchbuild.HitchBuild):
          def __init__(self, build_path, cpython):
              self.build_path = Path(build_path).abspath()
              self.fingerprint_path = self.build_path / "fingerprint.txt"
              self.logfile = self.build_path / ".." / "log.txt"
              self.thingfile = self.build_path / "virtualenv.txt"
              self.cpython = self.dependency(cpython)

          def build(self):
              if self.incomplete() or self.cpython.rebuilt:
                  if self.build_path.exists():
                      self.build_path.rmtree()
                  self.build_path.mkdir()
                  self.cpython.build.ensure_built()
                  self.thingfile.write_text("text\n", append=True)
                  self.logfile.write_text("virtualenv built\n", append=True)
                  self.refingerprint()

          def clean(self):
              self.build_path.rmtree()

      cpython = CPython("./python2.7.3")

      virtualenv = Virtualenv(
          "./venv",
          cpython=cpython,
      )



Dependency built:
  based on: dependency
  steps:
  - Run code: |
      virtualenv.ensure_built()
      virtualenv.ensure_built()

  - File contents will be:
      filename: log.txt
      text: |
        cpython built
        virtualenv built

  variations:
    When dependency is rebuilt rebuild children:
      steps:
      - Run code: |
          cpython.clean()
          virtualenv.ensure_built()

      - File contents will be:
          filename: log.txt
          text: |
            cpython built
            virtualenv built
            cpython built
            virtualenv built
