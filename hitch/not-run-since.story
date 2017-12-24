Not run since:
  based on: HitchBuild
  given:
    build.py: |
      import hitchbuild

      class BuildThing(hitchbuild.HitchBuild):
          def trigger(self):
              return self.monitor.not_run_since(seconds=1)

          def build(self):
              self.path.build.joinpath("thing.txt").write_text("oneline\n", append=True)

      def ensure_built():
          build_bundle = hitchbuild.BuildBundle(
              hitchbuild.BuildPath(build="."),
          )

          build_bundle['thing'] = BuildThing()
          build_bundle.ensure_built()
    setup: |
      from build import ensure_built
  steps:
    - Run code: |
        ensure_built()
        ensure_built()

    - File contents will be:
        filename: thing.txt
        text: |
          oneline

    - Sleep: 2

    - Run code: |
        ensure_built()

    - File contents will be:
        filename: thing.txt
        text: |
          oneline
          oneline
