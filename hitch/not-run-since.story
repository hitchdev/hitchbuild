Not run since:
  based on: HitchBuild
  #given:
    #setup: |
      #import hitchbuild
      #import hashlib

      #class Thing(hitchbuild.HitchBuild):
          #@property
          #def thingpath(self):
              #return self.build_path/"thing.txt"
      
          #def fingerprint(self):
              #return hashlib.sha1(self.thingpath.bytes()).hexdigest()

          #def build(self):
              #if self.monitor.not_run_since(seconds=1):
                  #self.thingpath.write_text("oneline\n", append=True)

      #build = Thing().with_build_path(".")
  #steps:
    #- Run code: |
        #build.ensure_built()
        #build.ensure_built()

    #- File contents will be:
        #filename: thing.txt
        #text: |
          #oneline

    #- Sleep: 2

    #- Run code: |
        #build.ensure_built()

    #- File contents will be:
        #filename: thing.txt
        #text: |
          #oneline
          #oneline
