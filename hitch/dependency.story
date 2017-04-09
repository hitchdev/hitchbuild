Dependency:
  based on: HitchBuild
  preconditions:
    files:
      build.py: |
        from hitchbuild import HitchBuild, needs

        class DependentThing(HitchBuild):
            def build(self):
                self.path.build.joinpath("dependentthing.txt").write_text("text")

        @needs(dependent_thing=DependentThing)
        class BuildThing(HitchBuild):
            def build(self):
                self.path.build.joinpath("thing.txt").write_text("text")

  scenario:
    - Run: |
        from build import BuildThing, DependentThing
        from hitchbuild import BuildPath

        BuildThing().requirement(dependent_thing=DependentThing())\
                    .in_path(BuildPath(build="."))\
                    .ensure_built()

    - File contents will be:
        filename: thing.txt
        reference: text
