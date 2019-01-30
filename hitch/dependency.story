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
              self.build_path = Path(build_path)
              self.fingerprint_path = self.build_path / "fingerprint.txt"
              self.thingfile = self.build_path / "cpython.txt"
              self.logfile = self.build_path / "log.txt"
              self.trigger(self.nonexistent(self.build_path))

          def build(self):
              if not self.build_path.exists():
                  self.build_path.mkdir()
              self.thingfile.write_text(
                  str(random.randrange(10**6, 10**7))
              )
              self.logfile.write_text("cpython built\n", append=True)

          def clean(self):
              if self.build_path.exists():
                  self.build_path.rmtree()


      class Virtualenv(hitchbuild.HitchBuild):
          def __init__(self, build_path, cpython):
              self.build_path = Path(build_path)
              self.fingerprint_path = self.build_path / "fingerprint.txt"
              self.logfile = self.build_path / "log.txt"
              self.thingfile = self.build_path / "virtualenv.txt"
              self.cpython = cpython
              self.trigger(self.dependency(cpython))
              self.trigger(self.nonexistent(self.build_path))

          def build(self):
              if not self.build_path.exists():
                  self.build_path.mkdir()
              self.cpython.ensure_built()
              self.thingfile.write_text("text\n", append=True)
              self.logfile.write_text("virtualenv built\n", append=True)

          def clean(self):
              self.build_path.rmtree()

      virtualenv = Virtualenv(
          "./venv",
          cpython=CPython("./python2.7.3")
      )



Dependency built:
  based on: dependency
  steps:
  - Run code: |
      virtualenv.ensure_built()
      virtualenv.ensure_built()

  - File contents will be:
      filename: venv/log.txt
      text: |
        virtualenv built

  variations:
    When dependency is rebuilt rebuild children:
      steps:
      - Run code: |
          virtualenv.cpython.clean()
          virtualenv.ensure_built()

      - File contents will be:
          filename: venv/log.txt
          text: |
            virtualenv built
            virtualenv built
