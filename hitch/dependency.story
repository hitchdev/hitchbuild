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

        thing = BuildThing().requirement(dependent_thing=DependentThing())
        thing.ensure_built(BuildPath(build="."))

    - File contents will be:
        filename: thing.txt
        reference: text
