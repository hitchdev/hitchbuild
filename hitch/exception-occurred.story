Exception occurred:
  based on: HitchBuild
  description: |
    If an exception occurs during a build, it is presumed that
    it needs to be run again, no matter what.
  given:
    files:
      sourcefile.txt: |
        file that, if changed, should trigger a rebuild
    setup: |
      from code_that_does_things import *
      import hitchbuild

      class Thing(hitchbuild.HitchBuild):
          @property
          def thingpath(self):
              return self.build_path/"thing.txt"

          def trigger(self):
              return self.monitor.non_existent(self.thingpath)

          def build(self):
              self.thingpath.write_text("oneline\n", append=True)

              raise ExampleException("build had an error")
  steps:
  - Exception raised with:
      code: |
        Thing().with_build_path(".").ensure_built()
      exception type: code_that_does_things.ExampleException
      message: build had an error

  - File contents will be:
      filename: thing.txt
      text: |
        oneline

  - Exception raised with:
      code: |
        Thing().with_build_path(".").ensure_built()
      exception type: code_that_does_things.ExampleException
      message: build had an error

  - File contents will be:
      filename: thing.txt
      text: |
        oneline
        oneline
