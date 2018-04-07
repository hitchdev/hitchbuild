Variable changed:
  based on: HitchBuild
  description: |
    Using HitchBuild you can feed an arbitrary variable into the
    build system and use it to determine whether or not to rebuild
    as well as how to rebuild.
    
    Some examples:
    
    - Building python virtualenv with a list of packages (all variables).
    - A version for the build itself (trigger a rebuild if the code has changed).
    
    HitchBuild will hash any variable it is passed to determine if it
    has changed. Any of the following or a combination
    are acceptable values - no other values are acceptable:
    
    * List
    * Dict
    * String
    * Float
    * Integer
    * Boolean
  given:
    files:
      sourcefile.txt: |
        the contents of this file, if changed, will trigger a rebuild.
    setup: |
      from path import Path
      import hitchbuild

      class Thing(hitchbuild.HitchBuild):
          def __init__(self, src_dir, variable_value):
              self._src_dir = Path(src_dir)
              self._variable_value = variable_value
              self._var_contents = self.monitored_vars(
                  var=self._variable_value,
              )

          @property
          def srcfile(self):
              return self._src_dir/"sourcefile.txt"

          def fingerprint(self):
              return self._variable_value

          @property
          def thingpath(self):
              return self.build_path/"thing.txt"

          def build(self):
              self.thingpath.write_text("build triggered\n", append=True)
              self.thingpath.write_text(
                  "vars changed: {0}\n".format(', '.join(self._var_contents.changes)),
                  append=True,
              )

  steps:
  - Run code: |
      Thing(".", ["1", "2", ]).with_build_path(".").ensure_built()
      Thing(".", ["1", "2", ]).with_build_path(".").ensure_built()

  - File contents will be:
      filename: thing.txt
      text: |
        build triggered
        vars changed: var
        build triggered
        vars changed: 

  - Run code: |
      Thing(".", ["1", "2", "3",]).with_build_path(".").ensure_built()

  - File contents will be:
      filename: thing.txt
      text: |-
        build triggered
        vars changed: var
        build triggered
        vars changed: 
        build triggered
        vars changed: var
        
  - Run code: |
      Thing(".", ["1", "2", "3",]).with_build_path(".").ensure_built()
      
  - File contents will be:
      filename: thing.txt
      text: |-
        build triggered
        vars changed: var
        build triggered
        vars changed: 
        build triggered
        vars changed: var
        build triggered
        vars changed: 
