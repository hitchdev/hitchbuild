File changed:
  based on: HitchBuild
  description: |
    For many builds (e.g. database, virtualenv), you will want
    to leave it be if it exists unless one or more source files have
    changed since the build was last run.
  given:
    files:
      sourcefile.txt: |
        file that, if changed, should trigger a rebuild
    setup: |
      from path import Path
      import hitchbuild

      class Thing(hitchbuild.HitchBuild):
          def __init__(self, src_dir):
              self._src_dir = Path(src_dir)

          def trigger(self):
              return self.monitor.non_existent(self.thingpath) | \
                  self.monitor.is_modified([self._src_dir/"sourcefile.txt"])
          
          @property
          def thingpath(self):
              return self.build_path/"thing.txt"

          def build(self):
              self.thingpath.write_text("build triggered\n", append=True)
              self.thingpath.write_text(
                  "files changed: {0}\n".format(', '.join(self.last_run.path_changes)),
                  append=True,
              )
              self.thingpath.write_text(
                  str(self.last_run.only.path_changes) + '\n',
                  append=True,
              )
              self.thingpath.write_text(
                  str("sourcefile.txt" in self.last_run.path_changes) + '\n',
                  append=True,
              )
              

      build = Thing(src_dir=".").with_build_path(".")
  steps:
  - Run code: |
      build.ensure_built()
      build.ensure_built()

  - File contents will be:
      filename: thing.txt
      text: |
        build triggered
        files changed: ./sourcefile.txt
        False
        True

  - Sleep: 1 

  - Touch file: sourcefile.txt

  - Run code: |
      build.ensure_built()

  - File contents will be:
      filename: thing.txt
      text: |-
        build triggered
        files changed: ./sourcefile.txt
        False
        True
        build triggered
        files changed: ./sourcefile.txt
        True
        True
