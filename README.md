The service layer provides a higher-level abstraction over the Client. It maps each API endpoint to a method on a Python class and sets the API base_url from the selected environment at initialization. Under the hood, it leverages the Client to perform all HTTP requests, keeping transport concerns (auth, retries, timeouts) centralized. This design simplifies API usage, enables IDE autocompletion, and adds type-checked interfaces to reduce mistakes when calling the API.
	•	Maps endpoints to class methods
	•	Derives base_url from the configured environment on init
	•	Delegates HTTP calls to the underlying Client (auth/retries/timeouts centralized)
	•	Enables autocompletion and type-checked calls for safer usage


The operations layer is the highest-level abstraction. It exposes a simple interface for business-level tasks—e.g., checking whether a data product has been modified, loading all entities from a data contract, or publishing a data product to Collibra from a data contract. It orchestrates one or more service calls, applies domain rules, handles errors/retries, and returns cohesive, typed results. Under the hood, it leverages the Service layer for all API queries, keeping transport details centralized in the Client.
	•	Provides task-oriented methods (e.g., check_data_product_modified, load_entities_from_contract, publish_to_collibra)
	•	Orchestrates multiple Service calls and enforces business rules
	•	Delegates all I/O to the Service/Client (no direct HTTP)
	•	Improves consistency, idempotency, and testability
	•	Returns domain objects/DTOs with clear types