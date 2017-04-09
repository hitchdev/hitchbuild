HitchBuild Quickstart:
  based on: HitchBuild
  preconditions:
    files:
      build.py: |
        from hitchbuild import HitchBuild
        from path import Path


        class BuildThing(HitchBuild):
            def build(self):
                self.path.build.joinpath("thing.txt").write_text("text")
  scenario:
    - Run: |
        from build import BuildThing
        from hitchbuild import BuildPath

        build = BuildThing()
        build.in_path(BuildPath(build=".")).ensure_built()

    - File contents will be:
        filename: thing.txt
        reference: text