File changed:
  based on: HitchBuild
  about: |
    For many builds (e.g. database, virtualenv), you will want
    to leave it be if it exists unless one or more source files have
    changed since the build was last run.
  given:
    files:
      requirements.txt: |
        file that, if changed, should trigger a reinstallation of requirements.
    setup: |
      from pathquery import pathquery
      from path import Path
      import hitchbuild


      class Virtualenv(hitchbuild.HitchBuild):
          def __init__(self, src_dir, build_dir):
              self._src_dir = Path(src_dir).abspath()
              self._build_dir = Path(build_dir).abspath()
              self.fingerprint_path = self._build_dir / "fingerprint.txt"
              self.reqs = self.source("reqs", [self._src_dir / "requirements.txt"])

          def log(self, message):
              self._build_dir.joinpath("..", "log.txt").write_text(message + '\n', append=True)

          def installreqs(self):
              self.log("pip install -r requirements.txt")

          def build(self):
              if self.incomplete():
                  if self._build_dir.exists():
                      self._build_dir.rmtree()
                  self._build_dir.mkdir()
                  self.log("create virtualenv")
                  self.installreqs()
              else:
                  if self.reqs.changed:
                      self.installreqs()

      virtualenv = Virtualenv(src_dir=".", build_dir="package")
  steps:
  - Run code: |
      virtualenv.ensure_built()
      virtualenv.ensure_built()

  - File contents will be:
      filename: log.txt
      text: |
        create virtualenv
        pip install -r requirements.txt

  - Sleep: 1

  - Touch file: requirements.txt

  - Run code: |
      virtualenv.ensure_built()

  - File contents will be:
      filename: log.txt
      text: |
        create virtualenv
        pip install -r requirements.txt
        pip install -r requirements.txt
