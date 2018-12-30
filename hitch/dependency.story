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
    files:
      special/specialbuildpath.txt: |
        This directory is where the special builds go.
    setup: |
      from path import Path
      import hitchbuild
      import hashlib
      import random

      class Dependency(hitchbuild.HitchBuild):
          def __init__(self, build_path):
              self._build_path = Path(build_path)
              self.build_database = self._build_path / "builddb.sqlite"

          @property
          def thingfile(self):
              return self._build_path / "dependentthing.txt"

          @property
          def log(self):
              return self._build_path / "log.txt"

          def build(self):
              if not self.thingfile.exists():
                  self.thingfile.write_text(
                      str(random.randrange(10**6, 10**7))
                  )
                  self.log.write_text("dependency task run\n", append=True)
                  self.generate_new_fingerprint()

          def clean(self):
              if self.thingfile.exists():
                  self.thingfile.remove()


      class Thing(hitchbuild.HitchBuild):
          def __init__(self, build_path, dependency):
              self.dependency = self.as_dependency(dependency)
              self._build_path = Path(build_path)
              self.build_database = self._build_path / "builddb.sqlite"

          @property
          def log(self):
              return self._build_path / "log.txt"

          @property
          def thingfile(self):
              return self._build_path / "thing.txt"

          def build(self):
              self.dependency.ensure_built()

              if self.dependency.rebuilt():
                  self.thingfile.write_text("text\n", append=True)
                  self.log.write_text("thing task run\n", append=True)

      thing = Thing(
          ".",
          dependency=Dependency(".")
      )



Dependency built:
  based on: dependency
  steps:
  - Run code: |
      thing.ensure_built()
      thing.ensure_built()

  - File contents will be:
      filename: log.txt
      text: |
        dependency task run
        thing task run

  variations:
    When dependency is rebuilt rebuild children:
      steps:
      - Run code: |
          thing.dependency.build.clean()
          thing.ensure_built()

      - File contents will be:
          filename: log.txt
          text: |
            dependency task run
            thing task run
            dependency task run
            thing task run
