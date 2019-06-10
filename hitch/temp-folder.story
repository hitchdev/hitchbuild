Temp folder:
  about: |
    Temporary folders are useful to do 
    By default, self.tmp is a Path object refering to /tmp folder.

    * If environment variable $TMP_FOLDER is set it will use that.
    * Unless, .with_tmp_folder(folder_path) is used, in which case that will be used instead.
  based on: HitchBuild
  given:
    setup: |
      from path import Path
      import hitchbuild

      class TempDirectoryUser(hitchbuild.HitchBuild):
          def build(self):
              print(self.tmp)

      temp_directory_user = TempDirectoryUser()
  variations:
    Default:
      steps:
      - Run code:
          code: temp_directory_user.ensure_built()
          will output: /tmp
