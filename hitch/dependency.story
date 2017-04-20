Dependency:
  based on: HitchBuild
  preconditions:
    files:
      build.py: |
        import hitchbuild

        class DependentThing(hitchbuild.HitchBuild):
            def build(self):
                self.path.build.joinpath("dependentthing.txt").write_text("text")

        @hitchbuild.needs(dependent_thing=DependentThing)
        class BuildThing(hitchbuild.HitchBuild):
            def build(self):
                self.path.build.joinpath("thing.txt").write_text("text")

        def ensure_built():
            build_bundle = hitchbuild.BuildBundle(
                hitchbuild.BuildPath(build="."),
                "db.sqlite"
            )

            build_bundle['dependent thing'] = DependentThing()
            build_bundle['thing'] = BuildThing().requirement(
                dependent_thing=build_bundle['dependent thing']
            )
            build_bundle.ensure_built()

  scenario:
    - Run: |
        from build import ensure_built

        ensure_built()

    - File contents will be:
        filename: thing.txt
        reference: text
