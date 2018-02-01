Non-existent build path:
  based on: quickstart
  steps:
  - Run code:
      code: |
        Thing().with_build_path("nonexistent").ensure_built()
      raises:
        type: hitchbuild.exceptions.BuildPathNonexistent
        message: |
          Cannot build. Build path '/path/to/nonexistent' nonexistent.
