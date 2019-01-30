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
      from collections import namedtuple

      dirs = namedtuple('PathGroup', ['gen',])(gen=Path("."))

      class Thing(hitchbuild.HitchBuild):
          def __init__(self, dirs):
              self.dirs = dirs
              self.trigger(self.nonexistent(self.thing))

          @property
          def thing(self):
              return self.dirs.gen.joinpath("thing.txt")

          def build(self):
              self.thing.write_text("text")

          def clean(self):
              self.thing.remove()
  steps:
  - Run code: |
      Thing(dirs).ensure_built()

  - File contents will be:
      filename: thing.txt
      text: text

  - Run code: |
      Thing(dirs).clean()

  - File does not exist: thing.txt
