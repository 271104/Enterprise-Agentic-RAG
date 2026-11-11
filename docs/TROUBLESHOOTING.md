# Troubleshooting

- **Startup reports missing settings:** provide `QDRANT_CLUSTER_ENDPOINT`, `PORTKEY_API_KEY`, and `GROQ_API_KEY`; also provide `GEMINI_API_KEY` when using the default provider.
- **Embedding error after switching providers:** the configured collection may use a different vector dimension. Recreate and reingest the collection with the selected provider.
- **No retrieved context:** confirm ingestion completed, the collection name matches `QDRANT_COLLECTION`, and the provider/dimension is unchanged. Qdrant failures now produce an API error rather than an empty search result.
- **DOCX/PPTX parsing dependency missing:** install the full local requirements; the API Docker image is not an ingestion image.
- **Streamlit cannot connect:** set `BACKEND_URL` to the API origin and confirm `/health/live` responds.
- **No Logfire or LangSmith traces:** those integrations are optional; verify their keys and tracing settings without pasting credentials into issue reports.
- **CI dependency audit reports an advisory:** review the exact dependency path and upstream advisory, update the compatible pin, then rebuild and rerun tests.
