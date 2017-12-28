Dependency:
  based on: HitchBuild
  given:
    setup: |
      import hitchbuild

      class DependentThing(hitchbuild.HitchBuild):
          @property
          def thingfile(self):
              return self.build_path/"dependentthing.txt"

          def trigger(self):
              return self.monitor.non_existent(self.thingfile)

          def build(self):
              self.thingfile.write_text("text\n", append=True)


      class Thing(hitchbuild.HitchBuild):
          def __init__(self, dependent_thing):
              self.dependent_thing = self.as_dependency(dependent_thing)
              
          @property
          def thingfile(self):
              return self.build_path/"thing.txt"

          def trigger(self):
              return self.monitor.non_existent(self.thingfile)

          def build(self):
              self.thingfile.write_text("text\n", append=True)
  steps:
    - Run code: |
        build = Thing(
            dependent_thing=DependentThing()
        ).with_build_path(".")

        build.ensure_built()
        build.ensure_built()

    - File contents will be:
        filename: thing.txt
        text: |
          text

    - File contents will be:
        filename: dependentthing.txt
        text: |
          text

    - Run code: |
        build = Thing(
            dependent_thing=DependentThing().triggered()
        ).with_build_path(".")

        build.ensure_built()

    - File contents will be:
        filename: thing.txt
        text: |
          text
          text

    - File contents will be:
        filename: dependentthing.txt
        text: |
          text
          text


