The client layer is the lowest-level abstraction. It provides a thin, explicit wrapper around HTTP (e.g., requests) so you can interact with the API directly while centralizing all transport concerns—authentication, certificates, retries, and timeouts. Higher layers (Service and Operations) build on top of the Client for all network I/O.
	•	Direct HTTP access: request, get, post, put, delete
	•	Centralized auth: API keys/bearer tokens/OAuth2 (with optional auto-refresh)
	•	TLS & certificates: CA bundles, custom certs, client certificates, verify/pinning controls
	•	Reliability: connection pooling, timeouts, retries with backoff, transient-error handling
	•	Consistency: shared base_url, default headers, JSON encode/decode, error mapping to exceptions
	•	Extras: pagination helpers, rate-limit/backoff handling, request/response logging & correlation IDs