# Operations

## Data and retention

The repository includes `DATA/noisy_data/`, described in its README as synthetic noise inspired by academic paper titles. The current Git revision also tracks six `DATA/true_data/` documents and eleven derived files under `processed_data/`; their redistribution rights are not confirmed. Do not publish this revision publicly until those files are rights-cleared or removed from the release commit. `.gitignore` prevents newly generated files from being added but does not untrack existing files. Avoid ingesting confidential material unless provider, database, and tracing data handling have been reviewed.

Ingestion writes chunk JSON locally and vector payloads to Qdrant. Removing local JSON does not remove vectors, and deleting a Qdrant collection removes indexed data. Back up or recreate the index from authorized sources as needed. The `--wipe` option is destructive.

## Logging and privacy

The API attaches request IDs and avoids placing raw query text in its own request logs. LangChain tracing may capture prompts when enabled; Logfire and provider-side logs have their own handling and retention. Do not enable tracing for sensitive workloads without reviewing those settings.

## Health and resource use

`/health/live` checks process responsiveness. `/health/ready` checks required configuration only. Model calls and Qdrant operations are synchronous; timeouts and provider limits can affect response latency. The conversation checkpoint is in process memory, has no expiry, and is lost on restart. Monitor memory use and do not run multiple workers when continuity across workers is expected.

## Incident response

If a credential is exposed, revoke and rotate it at its issuing provider, inspect repository history and logs, and notify affected operators. Report security issues privately as described in [SECURITY.md](../SECURITY.md).
