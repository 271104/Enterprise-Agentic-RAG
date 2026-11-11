# API reference

The API is served by `app.main:app`.

## `GET /health/live`

Returns `{"status":"ok"}` when the process can answer HTTP requests.

## `GET /health/ready`

Returns `{"status":"ready"}` when required configuration is present, or HTTP 503 otherwise. It does not ping external providers.

## `POST /query`

Request JSON:

```json
{"q":"question text","thread_id":"optional-private-session-id"}
```

`q` is trimmed and must be 1–8,000 characters. The whole request body is limited to 64 KiB. `thread_id` is optional and must be 1–128 characters when supplied. Omitting it creates a new UUID session. Unknown fields are rejected.

Response JSON contains `question`, `answer`, `thought_process`, `status`, `sources`, and `request_id`. The `X-Request-ID` response header carries the same request ID. Invalid input returns HTTP 422; processing errors return a generic HTTP 502 response. The error detail does not include upstream exception text.

## `GET /graph`

Returns a PNG visualization when graph rendering is available; otherwise returns HTTP 503.

There is no authentication or authorization. Do not expose the API publicly without an access-control layer appropriate to the deployment.
