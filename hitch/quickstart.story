Quickstart:
  based on: HitchBuild
  description: |
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

      class Thing(hitchbuild.HitchBuild):
          def __init__(self):
              pass

          @property
          def thingpath(self):
              return self.build_path/"thing.txt"
      
          def build(self):
              self.thingpath.write_text("text")
  steps:
  - Run code: |
      Thing().with_build_path(".").ensure_built()

  - File contents will be:
      filename: thing.txt
      reference: text
