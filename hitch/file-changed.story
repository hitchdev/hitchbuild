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
      import hitchbuild
      from pathquery import pathquery
      import hashlib

      class Thing(hitchbuild.HitchBuild):
          def __init__(self, src_dir):
              self._src = self.from_source(
                  pathquery(src_dir).named("sourcefile.txt"),
              )
          
          @property
          def thingpath(self):
              return self.build_path/"thing.txt"

          def fingerprint(self):
              return hashlib.sha1(self.thingpath.bytes()).hexdigest()

          def build(self):
              self.thingpath.write_text("build triggered\n", append=True)
              self.thingpath.write_text(
                  "files changed: {0}\n".format(', '.join(self._src.changes)),
                  append=True,
              )
              self.thingpath.write_text(
                  str("sourcefile.txt" in self._src.changes) + '\n',
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
        files changed: /path/to/sourcefile.txt
        True
        build triggered
        files changed: 
        False

  - Sleep: 1 

  - Touch file: sourcefile.txt

  - Run code: |
      build.ensure_built()

  - File contents will be:
      filename: thing.txt
      text: |-
        build triggered
        files changed: /path/to/sourcefile.txt
        True
        build triggered
        files changed: 
        False
        build triggered
        files changed: /path/to/sourcefile.txt
        True
