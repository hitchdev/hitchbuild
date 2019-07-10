Temp folder:
  about: |
    Temporary folder is
    By default, self.tmp is a Path.py object refering to /tmp folder.

    * If environment variable $TMP_FOLDER is set it will use that.
    * Unless, .with_tmp_folder(folder_path) is used, in which case that will be used instead.
  based on: HitchBuild
  given:
    setup: |
      from path import Path
      import hitchbuild

      class TempDirectoryUser(hitchbuild.HitchBuild):
          def __init__(self):
              self.fingerprint_path = self.tmp / "fingerprint.txt"

          def build(self):
              print(self.tmp / "mytempfile.txt")

      temp_directory_user = TempDirectoryUser()
  variations:
    Default:
      steps:
      - Run code:
          code: temp_directory_user.ensure_built()
          will output: /tmp/mytempfile.txt

    With environment variable:
      steps:
      - Run code:
          code: temp_directory_user.ensure_built()
          environment vars:
            TMP_FOLDER: /tmp/othertemp
          will output: /tmp/mytempfile.txt
