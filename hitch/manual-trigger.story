Manually trigger:
  based on: Skip if already built
  description: |
    While most automatic triggers may be sufficient to
    trigger a rebuild whenever it is necessary most of
    the time, a manual trigger will sometimes be necessary.
  scenario:
    - Run: |
        build_bundle().ensure_built()

    - File contents will be:
        filename: thing.txt
        text: oneline

    - Run: build_bundle().manually_trigger("thing").ensure_built()

    - File contents will be:
        filename: thing.txt
        text: |
          oneline
          oneline
