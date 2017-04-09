Skip if already built:
  based on: HitchBuild
  preconditions:
    files:
      build.py: |
        from hitchbuild import HitchBuild, built_if_exists

        @built_if_exists
        class BuildThing(HitchBuild):
            def exists(self):
                return self.path.build.joinpath("thing.txt").exists()

            def build(self):
                self.path.build.joinpath("thing.txt").write_text("oneline", append=True)

  scenario:
    - Run: |
        from build import BuildThing
        from hitchbuild import BuildPath

        thing = BuildThing().in_path(BuildPath(build="."))

        thing.ensure_built()
        thing.ensure_built()

    - File contents will be:
        filename: thing.txt
        text: oneline
