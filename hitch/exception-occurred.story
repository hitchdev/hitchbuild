Exception occurred:
  based on: HitchBuild
  description: |
    If an exception occurs during a build, it is presumed that
    it needs to be run again, no matter what.
  given:
    sourcefile.txt: |
      file that, if changed, should trigger a rebuild
    build.py: |
      from code_that_does_things import *
      import hitchbuild

      class BuildThing(hitchbuild.HitchBuild):
          def trigger(self):
              return self.monitor.non_existent(self.path.build.joinpath("thing.txt"))

          def build(self):
              self.path.build.joinpath("thing.txt").write_text("oneline\n", append=True)

              raise ExampleException("build had an error")

      def ensure_built():
          build_bundle = hitchbuild.BuildBundle(
              hitchbuild.BuildPath(build="."),
          )

          build_bundle['thing'] = BuildThing()
          build_bundle.ensure_built()
    setup: |
      from build import ensure_built
  steps:
  - Exception raised with:
      code: ensure_built()
      exception type: code_that_does_things.ExampleException
      message: build had an error

  - File contents will be:
      filename: thing.txt
      text: oneline

  - Exception raised with:
      code: ensure_built()
      exception type: code_that_does_things.ExampleException
      message: build had an error

  - File contents will be:
      filename: thing.txt
      text: |
        oneline
        oneline
