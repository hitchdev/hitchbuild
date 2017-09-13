File changed:
  based on: HitchBuild
  description: |
    For many builds (e.g. database, virtualenv), you will want
    to leave it be if it exists unless one or more files has
    changed since the build was last run.
  preconditions:
    sourcefile.txt: |
      file that, if changed, should trigger a rebuild
    build.py: |
      import hitchbuild

      class BuildThing(hitchbuild.HitchBuild):
          def trigger(self):
              return self.monitor.is_modified(["sourcefile.txt"])

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
  scenario:
    - Run code: |
        ensure_built()
        ensure_built()

    - File contents will be:
        filename: thing.txt
        text: oneline

    - Sleep: 1

    - Touch file: sourcefile.txt
 
    - Run code: |
        ensure_built()

    - File contents will be:
        filename: thing.txt
        text: |
          oneline
          oneline
