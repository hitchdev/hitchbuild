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
                self.path.build.joinpath("thing.txt").write_text("oneline\n", append=True)

        def build_bundle():
            bundle = hitchbuild.BuildBundle(
                hitchbuild.BuildPath(build="."),
                "db.sqlite"
            )

            bundle['thing'] = BuildThing()
            return bundle
  scenario:
    - Run: |
        from build import build_bundle

        build_bundle().ensure_built()
        build_bundle().ensure_built()

    - File contents will be:
        filename: thing.txt
        text: oneline
