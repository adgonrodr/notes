"""
DataProductOperations: business-level workflows for Collibra Data Contracts.

Defines :class:`DataProductOperations`, an operations-layer façade that exposes
task-oriented methods (not raw endpoints) to manage Collibra data products.
Use it to check changes, load entities from a contract, and publish to Collibra.
"""

from .base_operations import BaseOperations


class DataProductOperations(BaseOperations):
    """Task-focused operations for Collibra Data Contracts.

    Extends :class:`BaseOperations` and exposes business-level, end-to-end
    workflows to manage data products backed by Collibra Data Contracts. Instead
    of raw API calls, it orchestrates validations, lookups, mappings, and error
    handling so common outcomes can be triggered with a single method call
    (e.g., “check if a data product changed,” “load entities from a contract,”
    or “publish a data product to Collibra”).

    Internally, this class composes other operation-layer components (and, where
    needed, service-layer clients) to implement complete workflows—sequencing
    side effects, normalizing errors to domain exceptions, and emitting
    structured logs. Methods aim to be idempotent where practical.

    Attributes:
        logger (Logger): Logger for structured, contextual operation logs.
        services (ServicesFacade | None): Access to lower-level services, if used.
        ops (object | None): Internal helpers from the operations layer that this
            class leverages to compose end-to-end workflows.

    Examples:
        >>> ops = DataProductOperations(services=services, logger=logger)
        >>> changed = ops.is_modified_data_product("orders")
        >>> entities = ops.load_entities_from_contract("contracts/orders.yaml")
        >>> dp_id = ops.publish_data_product_by_contract("contracts/orders.yaml")

    See Also:
        BaseOperations: Common behavior for the operations layer (logging,
            error normalization, shared utilities).
    """
    ...

"""DataContractLoader: parse and resolve DMG Data Contracts.

Defines :class:`DataContractLoader`, which validates a data contract against the
DMG schemas (in the local ``schemas/`` folder), queries Collibra, and materializes
a :class:`DataProductInfo` plus a list of :class:`DataEntity` objects.
"""


class DataContractLoader:
    """Parser/loader for DMG Data Contracts that returns typed domain objects.

    Parses a data contract (YAML/JSON) that follows the DMG Data Contract
    specification, validates it against the bundled schemas in ``schemas/``,
    and uses the contract’s references to query Collibra for the data product
    and its assets. The loader returns a rich in-memory representation composed
    of a :class:`DataProductInfo` for the product-level metadata and a
    ``list[DataEntity]`` for the entities discovered.

    The class leverages :class:`DataProductStatusCalculator` to compute ETags
    and asset statuses, enabling efficient change detection and downstream
    publishing flows. Input validation is performed up front so callers receive
    consistent, typed results or domain errors (no partial/opaque responses).

    Attributes:
        schemas_path (str | pathlib.Path): Directory containing the DMG contract
            schemas used to validate input contracts.
        services (object): Collibra-facing service(s) used to perform lookups
            (e.g., assets, relations, attributes). Exact type depends on your
            service layer (e.g., ``ServicesFacade``).
        status_calculator (DataProductStatusCalculator): Component used to
            compute ETags and asset-level/product-level status.
        logger (Logger | None): Optional logger for structured diagnostics.

    Examples:
        >>> loader = DataContractLoader(
        ...     schemas_path="schemas/",
        ...     services=services,
        ...     status_calculator=status_calculator,
        ... )
        >>> dp_info, entities = loader.load("contracts/orders.yaml")
        >>> dp_info.slug
        'orders'
        >>> len(entities) > 0
        True

    Raises:
        ValidationError: If the data contract fails schema validation.
        LookupError: If required assets cannot be found in Collibra.
        CustomException: For domain-specific errors during mapping or status
            computation.

    See Also:
        DataProductStatusCalculator: Computes ETags and asset/product statuses.
        DataProductInfo: Pydantic model describing the data product metadata.
        DataEntity: Pydantic model representing a governed entity.
    """
    ...

"""DataProductLifecycleValidator: deployment-readiness checks for data products.

Defines :class:`DataProductLifecycleValidator`, an operations-layer validator
that decides if a data product can be deployed or promoted to a target
environment by reconciling local (computed) and remote (Collibra) statuses.
"""

from .base_operations import BaseOperations


class DataProductLifecycleValidator(BaseOperations):
    """Validate whether a data product can be deployed in a given environment.

    Extends :class:`BaseOperations` and evaluates lifecycle rules by comparing
    the locally computed status (e.g., from the current contract build) with the
    remote status recorded in Collibra. Each relevant asset is checked to
    ensure it is in a valid state to be changed or promoted, and any conflicts
    or violations are surfaced with actionable reasons.

    The validator is designed for task-oriented, business-level decisions
    (deploy / promote or not) rather than low-level endpoint calls. It
    orchestrates lookups, validations, mappings, and error normalization so
    callers receive a clear pass/fail outcome and a structured explanation.

    Attributes:
        logger (Logger): Logger used for structured diagnostics.
        services (ServicesFacade | None): Access to service-layer clients used
            to fetch remote status from Collibra and related metadata.

    Examples:
        >>> validator = DataProductLifecycleValidator(services=services, logger=logger)
        >>> result = validator.validate(environment="prod", local_status=local_status)
        >>> result.allowed
        True
        >>> result.reasons
        []

    Raises:
        ValidationError: If input preconditions are invalid (e.g., missing local status).
        CustomException: If lifecycle rules are violated or remote lookups fail.

    See Also:
        BaseOperations: Shared behavior for operations (logging, error handling).
        DataProductStatusCalculator: Component typically used to compute local status.
    """
    ...

"""DataProductPublisher: bulk publishing of Collibra metadata.

Defines :class:`DataProductPublisher`, an operations-layer publisher that
creates, updates, and removes Collibra assets for a data product. Uses the
Collibra async import job for bulk entity/attribute upserts and monitors job
completion.
"""

from .base_operations import BaseOperations


class DataProductPublisher(BaseOperations):
    """Publish, modify, and remove data product metadata in Collibra.

    Extends :class:`BaseOperations` to push a complete data product—its product
    record, entities, and attributes—into Collibra. The class collects and
    transforms typed inputs (e.g., ``DataProductInfo``, ``list[DataEntity]``,
    and related attribute payloads) into import-ready structures, submits an
    asynchronous bulk import job, and tracks that job to a verified outcome.
    It also performs targeted updates or deletions using the appropriate API
    endpoints when bulk import is not applicable.

    The publisher centralizes mapping, validation, error normalization, and
    status reporting so callers can trigger a single “publish” action rather
    than orchestrating low-level steps (payload shaping, job submission,
    polling, and result verification).

    Attributes:
        logger (Logger): Logger used for structured diagnostics.
        services (ServicesFacade | None): Access to service-layer clients for
            Collibra API calls and import job operations.
        job_poll_interval (float | None): Optional seconds between job status
            checks when monitoring async imports.
        job_timeout (float | None): Optional maximum seconds to wait for an
            async import job before timing out.

    Examples:
        >>> publisher = DataProductPublisher(services=services, logger=logger)
        >>> job_id = publisher.publish(
        ...     data_product=dp_info,
        ...     entities=entities,
        ...     attributes=attributes,
        ... )
        >>> result = publisher.wait_for_job(job_id)
        >>> result.success
        True

        # Removing assets (e.g., decommission flow)
        >>> publisher.remove_assets(asset_ids=["id:123", "id:456"])

    Raises:
        ValidationError: If required fields are missing or inputs fail pre-checks.
        LookupError: If referenced resources cannot be resolved in Collibra.
        TimeoutError: If the async import job does not complete within ``job_timeout``.
        CustomException: For domain-specific failures during mapping, submission,
            or job result reconciliation.

    See Also:
        BaseOperations: Shared behavior for logging, error handling, and utilities.
        DataContractLoader: Produces ``DataProductInfo`` and ``DataEntity`` inputs.
        DataProductLifecycleValidator: Verifies deploy/promote readiness before publish.
    """
    ...

"""DataProductStatusCalculator: local/remote status & ETag reconciliation.

Defines :class:`DataProductStatusCalculator`, an operations-layer helper that
computes local ETags and statuses and retrieves current Collibra asset status
to enable deterministic comparison with already-published assets.
"""

from .base_operations import BaseOperations


class DataProductStatusCalculator(BaseOperations):
    """Compute local ETags/status and fetch remote Collibra status for comparison.

    Extends :class:`BaseOperations` and provides utilities to:
    (1) derive deterministic, local ETags and per-asset status from a data
    contract and its resolved entities; (2) fetch the current, remote status
    for the corresponding Collibra assets; and (3) prepare both views for
    reliable, side-by-side comparison downstream (e.g., lifecycle validation,
    publish/no-op decisions, drift detection).

    The calculator centralizes hashing/normalization rules to ensure that
    ETag computation is stable across runs and environments. Remote lookups
    are abstracted behind the service layer so callers receive a typed, merged
    perspective suitable for diffing and decision-making.

    Attributes:
        logger (Logger): Logger used for structured, contextual diagnostics.
        services (ServicesFacade | None): Access to service-layer clients used
            to resolve Collibra asset identifiers and fetch remote statuses.
        hasher (object | callable | None): Optional strategy used to compute
            deterministic ETags from normalized payloads.

    Examples:
        >>> calc = DataProductStatusCalculator(services=services, logger=logger)
        >>> local = calc.compute_local_status(
        ...     data_product=dp_info,
        ...     entities=entities,
        ... )
        >>> remote = calc.fetch_remote_status(asset_keys=local.asset_keys)
        >>> # Consumers (e.g., validators/publishers) can now compare:
        >>> # diff = compare_status(local, remote)

    Raises:
        ValidationError: If input objects are incomplete or invalid for hashing.
        LookupError: If remote assets cannot be resolved or fetched from Collibra.
        CustomException: For domain-specific normalization or mapping failures.

    See Also:
        DataContractLoader: Produces the inputs (``DataProductInfo`` and entities)
            used for local status and ETag computation.
        DataProductLifecycleValidator: Uses local/remote views to decide whether
            a deploy/promotion is allowed.
        DataProductPublisher: Leverages status differences to determine upserts
            or removals during publish.
    """
    ...

operations (DataProductOperations): Business-level façade for data-product workflows (change, load, publish).
loader (DataContractLoader): Parses/validates DMG contracts; queries Collibra; returns DataProductInfo + entities.
validator (DataProductLifecycleValidator): Checks deploy/promote readiness via local vs remote status reconciliation.
publisher (DataProductPublisher): Bulk upserts/deletes via Collibra async import and job monitoring.
status_calculator (DataProductStatusCalculator): Computes ETags/local status and retrieves remote statuses for diffing.