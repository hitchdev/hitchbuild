Dependency:
  about: |
    Dependencies are builds which:
    
    * Must be built in order for another build to run.
    * Must, when rebuilt, trigger that other build to rerun.
    
    This example shows one build that, because it depends upon
    another, causes that build to be triggered.
    
    Then, the build is run again with the dependent build
    triggered manually. That causes the main build
    to be triggered.
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

Dependency built:
  based on: dependency
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


When dependency is triggered rebuild children:
  based on: dependency built
  steps:
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


