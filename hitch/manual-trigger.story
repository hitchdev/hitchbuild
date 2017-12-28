Manually trigger:
  based on: Skip if already built
  description: |
    While most automatic triggers may be sufficient to
    trigger a rebuild whenever it is necessary most of
    the time, a manual trigger will sometimes be necessary.
  steps:
  - Run code: |
      build.ensure_built()

  - File contents will be:
      filename: thing.txt
      text: |
        oneline

  - Run code: |
      build.triggered().ensure_built()

  - File contents will be:
      filename: thing.txt
      text: |
        oneline
        oneline
