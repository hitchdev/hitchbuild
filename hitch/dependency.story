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
      import hitchbuild
      import hashlib
      import random

      class Dependency(hitchbuild.HitchBuild):
          @property
          def thingfile(self):
              return self.build_path/"dependentthing.txt"

          @property
          def log(self):
              return self.build_path/"log.txt"
          
          def fingerprint(self):
              return hashlib.sha1(self.thingfile.bytes()).hexdigest()

          def build(self):
              if not self.thingfile.exists():
                  self.thingfile.write_text(
                      str(random.randrange(10**6, 10**7))
                  )
                  self.log.write_text("dependency task run\n", append=True)
          
          def clean(self):
              if self.thingfile.exists():
                  self.thingfile.remove()


      class Thing(hitchbuild.HitchBuild):
          def __init__(self, dependency):
              self.dependency = self.as_dependency(dependency)

          @property
          def log(self):
              return self.build_path/"log.txt"

          @property
          def thingfile(self):
              return self.build_path/"thing.txt"

          def fingerprint(self):
              return hashlib.sha1(self.thingfile.bytes()).hexdigest()

          def build(self):
              if not self.thingfile.exists() or self.dependency.rebuilt:
                  self.thingfile.write_text("text\n", append=True)
                  self.log.write_text("thing task run\n", append=True)


Dependency built:
  based on: dependency
  steps:
  - Run code: |
      build = Thing(
          dependency=Dependency()
      ).with_build_path(".")

      build.ensure_built()
      build.ensure_built()

  - File contents will be:
      filename: log.txt
      text: |
        dependency task run
        thing task run

  variations:
    When dependency is rebuilt rebuild children:
      steps:
      - Run code: |
          build = Thing(
              dependency=Dependency().with_build_path("."),
          ).with_build_path(".")

          build.dependency.clean()
          build.ensure_built()

      - File contents will be:
          filename: log.txt
          text: |
            dependency task run
            thing task run
            dependency task run
            thing task run

    When dependency has directory specified, use that one:
      steps:
      - Run code: |
          build = Thing(
              dependency=Dependency().with_build_path("special")
          ).with_build_path(".")

          build.ensure_built()
          build.ensure_built()
          
      - File exists: special/dependentthing.txt
      
      - File contents will be:
          filename: special/log.txt
          text: |
            dependency task run

      - File contents will be:
          filename: log.txt
          text: |
            dependency task run
            thing task run
            thing task run
            
