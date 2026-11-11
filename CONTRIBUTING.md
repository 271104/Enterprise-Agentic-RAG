# Contributing

Thanks for contributing. Keep changes focused and preserve existing behavior unless the change has a clear reason. Do not commit credentials, generated environments, or unlicensed data.

## Development

Use Python 3.11 and follow the root README setup. Add or update mocked tests for code changes; tests must not require paid model credentials or live external services.

Before submitting, run:

```sh
python -m pytest
ruff check app evals ui tests
ruff format --check app evals ui tests
```

Describe behavior changes, configuration changes, tests actually run, and known limitations in the pull request. Avoid sharing real prompts, documents, secrets, or trace data in issues.
