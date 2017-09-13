Dependency:
  based on: HitchBuild
  preconditions:
    build.py: |
      import hitchbuild

      class DependentThing(hitchbuild.HitchBuild):
          def trigger(self):
              return self.monitor.non_existent(self.path.build.joinpath("dependentthing.txt"))

          def build(self):
              self.path.build.joinpath("dependentthing.txt").write_text("text\n", append=True)

      @hitchbuild.needs(dependent_thing=DependentThing)
      class BuildThing(hitchbuild.HitchBuild):
          def __init__(self, dependent_thing):
              super(BuildThing, self).__init__()
              self._requirements = {"dependent_thing": dependent_thing}

          def trigger(self):
              return self.monitor.non_existent(self.path.build.joinpath("thing.txt"))

          def build(self):
              self.path.build.joinpath("thing.txt").write_text("text\n", append=True)

      def build_bundle():
          bundle = hitchbuild.BuildBundle(
              hitchbuild.BuildPath(build="."),
              "db.sqlite"
          )

          bundle['dependent thing'] = DependentThing()
          bundle['thing'] = BuildThing(bundle['dependent thing'])
          return bundle
    setup: |
      from build import build_bundle

      bundle = build_bundle()
  scenario:
    - Run code: |
        bundle.ensure_built()
        bundle.ensure_built()

    - File contents will be:
        filename: thing.txt
        text: |
          text

    - File contents will be:
        filename: dependentthing.txt
        text: |
          text

    - Run code: |
        bundle.manually_trigger("dependent thing").ensure_built()

    - File contents will be:
        filename: dependentthing.txt
        text: |
          text
          text

    - File contents will be:
        filename: thing.txt
        text: |
          text
          text

