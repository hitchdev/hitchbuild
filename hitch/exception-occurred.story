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
      import hitchbuild

      class Thing(hitchbuild.HitchBuild):
          @property
          def thingpath(self):
              return self.build_path/"thing.txt"

          def build(self):
              self.thingpath.write_text("oneline\n", append=True)

              raise Exception("build had an error")
  steps:
  - Run code:
      code: |
        Thing().with_build_path(".").ensure_built()
      raises:
        type: builtins.Exception
        message: build had an error

  - File contents will be:
      filename: thing.txt
      text: |
        oneline

  - Run code:
      code: |
        Thing().with_build_path(".").ensure_built()
      raises:
        type: builtins.Exception
        message: build had an error

  - File contents will be:
      filename: thing.txt
      text: |
        oneline
        oneline
