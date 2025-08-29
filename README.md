# Operations Layer

The operations let you work in business terms rather than raw API calls. You trigger outcomes like "check if a data product changed," "load entities from a contract", or "publish a data product to Collibra", and the layer takes care of all the lookups, validations, mappings, and error handling for you.   

Under the hood it coordinates the Service layer so results are consistent and repeatable across environments.

⸻

# Available operations

## Data Product Operations

### Check if a data product has been modified

#### What it does (functional):
Tells you whether a data product has changed since a reference point, and—if you want—what changed (schema, metadata, ownership, tags).

Typical uses:
- Trigger a publish or a validation only when something actually changed.
- Build dashboards or alerts that flag meaningful updates.

Inputs (most common):
- Data product identifier (name or ID).
- Reference (either a timestamp like “since 2025-08-01” or a prior fingerprint/hash).
- Include details? Ask for a change summary and schema diff when needed.

Output:
- True/False for a quick check, or a change report (e.g., what parts changed, a short summary, a current hash you can store).

⸻

### Publish a data product from a Data Contract (to Collibra)

What it does (functional):
Takes a Data Contract and publishes/updates the corresponding assets and relationships in Collibra. You can preview the plan (no changes) or execute it.

Typical uses:
- Roll out a new data product or apply contract-driven updates.
- Promote changes through DEV/UAT/PROD in a controlled, auditable way.

Inputs (most common):
- Data Contract (object, YAML/JSON file path, or dict).
- Target environment (e.g., DEV, UAT, PROD).
- Mode:
- Dry-run — see the change plan without making changes.
- Force — attempt conflict resolution (rename/relink) if needed.

Output:
- A publish result showing created, updated, skipped, and warnings, plus a plan when running in dry-run.

⸻

### Load entities from a Data Contract

What it does (functional):
Reads a Data Contract and returns a clean list of entities (and their columns/metadata) you can use for docs, validation, diffs, or publishing.

Typical uses:
- Generate documentation or schema catalogs.
- Compare contract versions or validate downstream systems.
- Feed publishing or lineage jobs with a typed model of entities.

Inputs (most common):
- Data Contract (object, YAML/JSON file path, or dict).
- Include system entities? Optional flag to include internal/template entities.

Output:
- A typed list of entities with names, columns, types, nullability, descriptions, and other metadata.
