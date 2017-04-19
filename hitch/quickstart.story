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
  preconditions:
    files:
      build.py: |
        import hitchbuild


        class BuildThing(hitchbuild.HitchBuild):
            def build(self):
                self.path.build.joinpath("thing.txt").write_text("text")

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

        ensure_built()

    - File contents will be:
        filename: thing.txt
        reference: text
