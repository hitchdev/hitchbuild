Skip if already built:
  based on: HitchBuild
  preconditions:
    files:
      build.py: |
        import hitchbuild


        class BuildThing(hitchbuild.HitchBuild):
            def trigger(self):
                return self.monitor.non_existent(self.path.build.joinpath("thing.txt"))

            def build(self):
                self.path.build.joinpath("thing.txt").write_text("oneline", append=True)

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
        ensure_built()

    - File contents will be:
        filename: thing.txt
        text: oneline
