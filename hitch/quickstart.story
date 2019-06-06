Quickstart:
  based on: HitchBuild
  about: |
    HitchBuild is a simple set of tools for performing
    common build tasks.

    The simplest build you can build is as follows, which
    will run "build" whenever .ensure_built() is called
    which, in this case, will simply make the text file
    "thing.txt" in the build directory contain the text
    "text".
  given:
    setup: |
      import hitchbuild
      from path import Path

      class Thing(hitchbuild.HitchBuild):
          def __init__(self, build_dir):
              self._build_dir = Path(build_dir).abspath()
              self.fingerprint_path = self._build_dir / "fingerprint.txt"

          @property
          def thing(self):
              return self._build_dir / "thing.txt"

          def build(self):
              self.clean()
              self._build_dir.mkdir()
              self.thing.write_text("text")

          def clean(self):
              if self._build_dir.exists():
                  self._build_dir.rmtree()
  steps:
  - Run code: |
      Thing("gen").ensure_built()

  - File contents will be:
      filename: gen/thing.txt
      text: text

  - Run code: |
      Thing("gen").clean()

  - File does not exist: thing.txt
