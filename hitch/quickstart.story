Quickstart:
  based on: HitchBuild
  description: |
    HitchBuild is a simple set of tools for performing
    common build tasks.
    
    The simplest build you can build is as follows, which
    will run "build" whenever .ensure_built() is called
    which, in this case, will simply make the text file
    "thing.txt" in the build directory contain the text
    "text".
  preconditions:
    files:
      build.py: |
        import hitchbuild

        class BuildThing(hitchbuild.HitchBuild):
            def trigger(self):
                return self.monitor.non_existent(self.path.build.joinpath("thing.txt"))
        
            def build(self):
                self.path.build.joinpath("thing.txt").write_text("text")

        def build_bundle():
            bundle = hitchbuild.BuildBundle(
                hitchbuild.BuildPath(build="."),
                "db.sqlite"
            )

            bundle['thing'] = BuildThing()
            return bundle
  scenario:
    - Run: |
        from build import build_bundle

        build_bundle().ensure_built()

    - File contents will be:
        filename: thing.txt
        reference: text
