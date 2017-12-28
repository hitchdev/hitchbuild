Skip if already built:
  based on: HitchBuild
  given:
    setup: |
      import hitchbuild


      class Thing(hitchbuild.HitchBuild):
          def __init__(self):
              pass

          def trigger(self):
              return self.monitor.non_existent(self.thingpath)

          @property
          def thingpath(self):
              return self.build_path/"thing.txt"
      
          def build(self):
              self.thingpath.write_text("oneline\n", append=True)
      
      build = Thing().with_build_path(".")
  steps:
    - Run code: |
        build.ensure_built()
        build.ensure_built()

    - File contents will be:
        filename: thing.txt
        text: |
          oneline
