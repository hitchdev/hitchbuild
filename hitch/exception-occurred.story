Exception occurred:
  based on: HitchBuild
  description: |
    If an exception occurs during a build, it is presumed that
    it needs to be run again, no matter what.
  preconditions:
    files:
      sourcefile.txt: |
        file that, if changed, should trigger a rebuild
      build.py: |
        from code_that_does_things import *
        import hitchbuild

        @hitchbuild.built_if_exists
        class BuildThing(hitchbuild.HitchBuild):
            def exists(self):
                return self.path.build.joinpath("thing.txt").exists()

            def build(self):
                self.path.build.joinpath("thing.txt").write_text("oneline\n", append=True)

                raise ExampleException("build had an error")

        def ensure_built():
            build_bundle = hitchbuild.BuildBundle(
                hitchbuild.BuildPath(build="."),
                "db.sqlite"
            )

            build_bundle['thing'] = BuildThing()
            build_bundle.ensure_built()
  scenario:
    - Run: |
        from build import ensure_built

    - Exception is raised:
        command: ensure_built()
        exception: build had an error

    - File contents will be:
        filename: thing.txt
        text: oneline

    - Exception is raised:
        command: ensure_built()
        exception: build had an error

    - File contents will be:
        filename: thing.txt
        text: |
          oneline
          oneline
