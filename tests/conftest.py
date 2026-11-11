import os

# Unit tests intentionally run without an observability backend.
os.environ.setdefault("LOGFIRE_IGNORE_NO_CONFIG", "1")
