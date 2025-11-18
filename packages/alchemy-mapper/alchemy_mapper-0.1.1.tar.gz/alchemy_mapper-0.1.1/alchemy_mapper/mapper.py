"""
SQLAlchemy Core to Pydantic Mapper (Async-Only).

Async read-side query mapper for CQRS pattern that executes SQLAlchemy Core queries
and maps results to Pydantic models.

Features:
- Async/await query execution
- Memory-efficient async streaming
- Nested model mapping via __ convention
- Works with async read replicas
- Framework-agnostic
- Pydantic-only (simplified and optimized)
- Supports both raw SQL strings and SQLAlchemy Core statements

⚠️  SECURITY WARNING:
    When using raw SQL strings, ALWAYS use parameterized queries to prevent SQL injection:

    ✅ SAFE:
        mapper.query[User]("SELECT * FROM users WHERE id = :id", {"id": user_id})

    ❌ UNSAFE (DO NOT DO THIS):
        mapper.query[User](f"SELECT * FROM users WHERE id = {user_id}")

Example Usage:
    # Recommended: Use with AsyncReadOnlyUnitOfWork
    from scaffold.project_templates.fastapi.infrastructure.readonly_uow import AsyncReadOnlyUnitOfWork

    async with AsyncReadOnlyUnitOfWork(engine) as uow:
        mapper = AlchemyMapper(conn)
        users = await mapper.query[list[User]]("SELECT * FROM users")

    # Raw SQL with parameters (ALWAYS USE PARAMETERS!)
    async with AsyncReadOnlyUnitOfWork(engine) as uow:
        mapper = AlchemyMapper(conn)
        user = await mapper.query[User](
            "SELECT * FROM users WHERE id = :id",
            params={"id": 123}
        )

    # SQLAlchemy Core statements
    from sqlalchemy import select, bindparam
    stmt = select(users).where(users.c.id == bindparam('id'))
    user = await mapper.query[User](stmt, params={"id": 123})

    # Async streaming for large result sets
    async with AsyncReadOnlyUnitOfWork(engine) as uow:
        mapper = AlchemyMapper(conn)
        async for user in mapper.stream[User](sql):
            await process(user)

    # Nested models using __ convention
    stmt = select(
        users.c.id,
        users.c.name,
        profiles.c.bio.label("profile__bio"),
        profiles.c.avatar.label("profile__avatar")
    )
    users = await mapper.query[list[UserWithProfile]](stmt)

    # With custom NULL handling
    mapper = AlchemyMapper(conn, null_strategy='omit')
"""

import logging
import time
from collections import defaultdict
from collections.abc import AsyncIterator, Callable
from contextlib import contextmanager
from functools import lru_cache
from typing import (
    Any,
    Literal,
    TypeVar,
    get_args,
    get_origin,
)

try:
    from pydantic import BaseModel

    PYDANTIC_AVAILABLE = True
except ImportError:
    BaseModel = None
    PYDANTIC_AVAILABLE = False

try:
    import sqlalchemy
    from sqlalchemy import text
    from sqlalchemy.exc import SQLAlchemyError
    from sqlalchemy.ext.asyncio import AsyncConnection
    from sqlalchemy.sql import Select
    from sqlalchemy.sql.elements import TextClause

    # Version check
    SA_VERSION = tuple(int(x) for x in sqlalchemy.__version__.split(".")[:2])
    if SA_VERSION < (2, 0):
        raise ImportError(
            f"SQLAlchemy 2.0+ required, found {sqlalchemy.__version__}. "
            "Upgrade with: pip install 'sqlalchemy>=2.0'"
        )
except ImportError as exc:
    raise ImportError(
        "SQLAlchemy 2.0+ is required for AlchemyMapper. "
        "Install it with: pip install 'sqlalchemy>=2.0'"
    ) from exc


T = TypeVar("T")

# Module-level logger
logger = logging.getLogger(__name__)


class PydanticMapperError(Exception):
    """Base exception for AlchemyMapper errors."""


class QueryExecutionError(PydanticMapperError):
    """Raised when query execution fails."""


class MappingError(PydanticMapperError):
    """Raised when result mapping fails."""


class ValidationError(PydanticMapperError):
    """Raised when model validation fails."""


class _AsyncMethodProxy:
    """Generic proxy for subscriptable async methods (query/stream)."""

    __slots__ = ("_target_type", "mapper", "method_name")

    def __init__(self, mapper: "AlchemyMapper", method_name: str):
        self.mapper = mapper
        self.method_name = method_name
        self._target_type = None

    def __getitem__(self, item):
        """Support mapper.method[Type] syntax."""
        self._target_type = item
        return self

    async def __call__(self, *args, **kwargs):
        """Execute the async method with stored type."""
        if self._target_type is not None:
            self.mapper._target_type = self._target_type

        try:
            method = getattr(self.mapper, f"_{self.method_name}_impl")
            result = await method(*args, **kwargs)

            # Handle both regular async and async generators
            if hasattr(result, "__aiter__"):
                async for item in result:
                    yield item
            else:
                # For non-generator results, wrap in a generator
                yield result
        finally:
            self.mapper._target_type = None
            self._target_type = None


class AlchemyMapper:
    """
    AlchemyMapper - Async-only read-side query mapper for CQRS pattern.

    Executes SQLAlchemy Core queries asynchronously and maps results to
    Pydantic models. Supports streaming and nested model mapping.

    This is a read-only tool designed for the query side of CQRS.
    Use with async read replicas for optimal performance.

    Note:
    - Only supports Pydantic models for simplified and optimized performance.
    - Validation is disabled globally for performance (uses model_construct()).
    - Safe for database queries where data is already validated/stored correctly.
    - Requires SQLAlchemy 2.0+
    """

    # Configurable cache sizes for LRU caches
    TYPE_INFO_CACHE_SIZE = 256
    NESTED_STRUCTURE_CACHE_SIZE = 64
    FIELD_TYPE_CACHE_SIZE = 512
    PYDANTIC_CHECK_CACHE_SIZE = 256

    def __init__(
        self,
        async_connection: AsyncConnection,
        custom_logger: logging.Logger | None = None,
        log_level: int = logging.DEBUG,
        null_strategy: Literal["none", "omit", "default"] = "none",
        metrics_callback: Callable[[dict[str, Any]], None] | None = None,
    ):
        """
        Initialize mapper with async SQLAlchemy connection.

        Args:
            async_connection: AsyncConnection from SQLAlchemy (NOT AsyncEngine)
            custom_logger: Optional custom logger instance (defaults to module logger)
            log_level: Logging level for query operations (defaults to DEBUG)
            null_strategy: How to handle NULL values:
                - 'none': Keep as None (default)
                - 'omit': Remove NULL fields from result
                - 'default': Use model defaults for NULL values
            metrics_callback: Optional callback function for query metrics
                Will be called with dict containing query_time, row_count, model, etc.

        Examples:
            # Recommended: Use with AsyncReadOnlyUnitOfWork (CQRS pattern)
            from scaffold.project_templates.fastapi.infrastructure.readonly_uow import AsyncReadOnlyUnitOfWork

            async with AsyncReadOnlyUnitOfWork(engine) as uow:
                mapper = AlchemyMapper(conn)
                users = await mapper.query[list[User]]("SELECT * FROM users")

            # Alternative: Manage connection manually
            from sqlalchemy.ext.asyncio import create_async_engine
            engine = create_async_engine("postgresql+asyncpg://...")

            async with engine.connect() as conn:
                mapper = AlchemyMapper(conn)
                users = await mapper.query[list[User]]("SELECT * FROM users")

            # With custom logger and NULL handling
            import logging
            custom_logger = logging.getLogger('my_app.queries')
            async with engine.connect() as conn:
                mapper = AlchemyMapper(
                    conn,
                    custom_logger=custom_logger,
                    log_level=logging.INFO,
                    null_strategy='omit'
                )

            # With metrics callback
            def track_metrics(metrics):
                print(f"Query took {metrics['query_time']:.3f}s, {metrics['row_count']} rows")

            async with engine.connect() as conn:
                mapper = AlchemyMapper(conn, metrics_callback=track_metrics)
        """
        # Validate connection type
        if not isinstance(async_connection, AsyncConnection):
            raise TypeError(
                f"Expected AsyncConnection, got {type(async_connection).__name__}. "
                "Tip: Use engine.connect() or engine.begin() to get an AsyncConnection."
            )

        self.connection = async_connection
        self.logger = custom_logger if custom_logger is not None else logger
        self.log_level = log_level
        self.null_strategy = null_strategy
        self.metrics_callback = metrics_callback
        self._target_type = None
        self._field_mapping = None
        self._nested_mapping = None

        # Create proxy objects for subscriptable syntax
        self.query = _AsyncMethodProxy(self, "query")
        self.stream = _AsyncMethodProxy(self, "stream")

    @contextmanager
    def override_connection(self, test_connection: AsyncConnection):
        """
        Override connection for testing purposes.

        Args:
            test_connection: Test connection to use instead of the real one

        Example:
            mapper = AlchemyMapper(real_connection)
            with mapper.override_connection(mock_connection):
                # Use mapper with mock_connection
                result = await mapper.query[User]("SELECT * FROM users")
        """
        old_conn = self.connection
        self.connection = test_connection
        try:
            yield
        finally:
            self.connection = old_conn

    async def explain(
        self, sql: str | Select | TextClause, params: dict[str, Any] | None = None
    ) -> list[dict]:
        """
        Return query execution plan without executing the query.

        Useful for debugging and optimization.

        Args:
            sql: SQL query to explain
            params: Query parameters

        Returns:
            List of dicts containing execution plan

        Example:
            plan = await mapper.explain("SELECT * FROM users WHERE id = :id", {"id": 123})
            print(plan)
        """
        explain_sql = f"EXPLAIN {sql}" if isinstance(sql, str) else text(f"EXPLAIN {sql}")

        result = await self._execute_query(explain_sql, params)
        rows = result.fetchall() if hasattr(result, "fetchall") else await result.all()
        return [self._row_to_dict(row) for row in rows]

    async def _query_impl(
        self,
        sql: str | Select | TextClause,
        params: dict[str, Any] | None = None,
        field_mapping: dict[str, str] | None = None,
        nested_mapping: dict[str, list[str]] | None = None,
    ):
        """
        Execute async query and return mapped results.

        Type inference from generic parameter:
        - await query[list[User]](sql) -> list[User]
        - await query[User](sql) -> User | None
        - await query(sql) -> list[dict]

        Examples:
            users = await mapper.query[list[User]]("SELECT * FROM users")
            user = await mapper.query[User]("SELECT * FROM users WHERE id = 1")
        """

        # Store mappings
        self._field_mapping = field_mapping
        self._nested_mapping = nested_mapping

        # Start timing
        start_time = time.perf_counter()

        try:
            # Extract type information
            model_class, _, is_single = self._extract_type_info()

            # Validate model_class if provided
            if model_class is not None:
                self._validate_model_class(model_class)

            # Log query start (conditional logging)
            if self.logger.isEnabledFor(self.log_level):
                model_name = model_class.__name__ if model_class else "dict"
                log_msg = f"Executing query [model={model_name}]: {sql}"
                if params:
                    log_msg += f"\nQuery params: {params}"
                self.logger.log(self.log_level, log_msg)

            # Execute query
            query_start = time.perf_counter()
            result = await self._execute_query(sql, params)
            query_time = time.perf_counter() - query_start

            # Map results
            mapping_start = time.perf_counter()

            if model_class is None:
                # Auto-mapping mode (optimized row-to-dict conversion)
                rows = result.fetchall() if hasattr(result, "fetchall") else await result.all()
                mapped_results = [self._row_to_dict(row) for row in rows]
                row_count = len(mapped_results)
                final_result = mapped_results
            else:
                # Fetch all rows
                rows = result.fetchall() if hasattr(result, "fetchall") else await result.all()

                # Batch instantiation optimization for Pydantic
                # Note: Only use batch optimization for simple cases without nested mapping
                # For nested mapping, use per-row processing to ensure correctness
                use_batch = (
                    self._is_pydantic_cached(model_class)
                    and not self._field_mapping
                    and not self._nested_mapping
                )

                if use_batch:
                    # Simple batch validation - convert all rows to dicts, then validate
                    row_dicts = [self._row_to_dict(row) for row in rows]
                    # Check if nested mapping is needed (auto-detect)
                    needs_nested = any("__" in str(k) for d in row_dicts for k in d)

                    if needs_nested:
                        # Fall back to per-row processing for nested mapping
                        mapped_results = []
                        for row in rows:
                            mapped_results.append(self._map_row(row, model_class))
                    else:
                        # Batch construct (skip validation for performance)
                        mapped_results = [model_class.model_construct(**d) for d in row_dicts]
                else:
                    # For cases with field/nested mapping, map one by one
                    mapped_results = []
                    for row in rows:
                        mapped_results.append(self._map_row(row, model_class))

                row_count = len(mapped_results)

                # Return based on type
                if is_single:
                    final_result = mapped_results[0] if mapped_results else None
                else:
                    final_result = mapped_results

            mapping_time = time.perf_counter() - mapping_start
            total_time = time.perf_counter() - start_time

            # Log completion (conditional logging)
            if self.logger.isEnabledFor(self.log_level):
                self.logger.log(
                    self.log_level,
                    f"Query completed: {row_count} rows, "
                    f"exec={query_time:.3f}s, map={mapping_time:.3f}s, total={total_time:.3f}s",
                )

            # Call metrics callback if provided
            if self.metrics_callback:
                metrics = {
                    "query_time": query_time,
                    "mapping_time": mapping_time,
                    "total_time": total_time,
                    "row_count": row_count,
                    "model": model_class.__name__ if model_class else "dict",
                    "is_single": is_single,
                }
                try:
                    self.metrics_callback(metrics)
                except Exception as e:
                    self.logger.warning(f"Metrics callback failed: {e}")

            return final_result

        finally:
            self._field_mapping = None
            self._nested_mapping = None

    def _validate_model_class(self, model_class: Any) -> None:
        """Validate that model_class is a valid Pydantic model."""
        if not isinstance(model_class, type):
            raise ValidationError(
                f"Expected a class type, got {type(model_class).__name__}: {model_class}"
            )

        if not self._is_pydantic_cached(model_class):
            raise ValidationError(
                f"{model_class.__name__} is not a Pydantic model. "
                "AlchemyMapper only supports Pydantic BaseModel classes."
            )

        # Check for model_construct method (Pydantic v2)
        if not hasattr(model_class, "model_construct"):
            raise ValidationError(
                f"{model_class.__name__} doesn't support model_construct. "
                "Ensure it's a Pydantic v2 model."
            )

    @staticmethod
    @lru_cache(maxsize=256)  # Use class constant in production
    def _extract_type_info_cached(target_type) -> tuple[type | None, bool, bool]:
        """
        Extract type information from generic parameter (cached).

        Returns:
            (model_class, is_list, is_single)

        Examples:
            list[User] -> (User, True, False)
            User -> (User, False, True)
            None -> (None, False, False)
        """
        if target_type is None:
            return None, False, False

        origin = get_origin(target_type)
        args = get_args(target_type)

        # Check for list[T]
        if origin is list and args:
            return args[0], True, False

        # Single type T
        return target_type, False, True

    def _extract_type_info(self) -> tuple[type | None, bool, bool]:
        """
        Extract type information from generic parameter.

        Returns:
            (model_class, is_list, is_single)
        """
        if self._target_type is None:
            return None, False, False

        return self._extract_type_info_cached(self._target_type)

    def _row_to_dict(self, row) -> dict:
        """Optimized row-to-dict conversion with NULL handling."""
        # Try faster methods first
        if hasattr(row, "_asdict"):
            data = row._asdict()
        elif hasattr(row, "_mapping"):
            # Direct dict cast is faster than dict comprehension
            data = dict(row._mapping)
        else:
            # Fallback to dict constructor
            data = dict(row)

        # Apply NULL strategy
        if self.null_strategy == "omit":
            return {k: v for k, v in data.items() if v is not None}

        return data

    async def _execute_query(self, sql, params):
        """Execute query asynchronously with validation and error handling."""
        # Input validation
        if not sql:
            raise QueryExecutionError("SQL query cannot be empty")

        if not isinstance(sql, (str, Select, TextClause)):
            raise QueryExecutionError(
                f"Invalid SQL type: {type(sql).__name__}. Expected str, Select, or TextClause"
            )

        try:
            if isinstance(sql, str):
                sql = text(sql)
            return await self.connection.execute(sql, params or {})
        except SQLAlchemyError as e:
            # Specific SQLAlchemy errors
            raise QueryExecutionError(f"Database query failed: {e}") from e
        except (ValueError, TypeError) as e:
            # Parameter-related errors
            raise QueryExecutionError(f"Query parameter error: {e}") from e
        except Exception as e:
            # Unexpected errors
            raise QueryExecutionError(f"Unexpected query error: {e}") from e

    def _map_row(self, row, model_class: type):
        """
        Map a single row to the target Pydantic model.

        Handles:
        - Field mapping
        - Nested model mapping (__ convention)
        - Pydantic model construction (validation disabled for performance)

        Args:
            row: Database row
            model_class: Target Pydantic model class
        """
        try:
            # Convert row to dict (optimized)
            row_dict = self._row_to_dict(row)

            # Apply field mapping
            if self._field_mapping:
                row_dict = self._apply_field_mapping(row_dict)

            # Apply nested mapping if needed (check only once)
            if self._nested_mapping or any("__" in key for key in row_dict):
                row_dict = self._apply_nested_mapping(
                    row_dict, self._nested_mapping or {}, model_class
                )

            # Map to Pydantic model
            return self._map_to_pydantic(row_dict, model_class)

        except (MappingError, ValidationError):
            # Re-raise our own exceptions without modification
            raise
        except Exception as e:
            # Enhance error message with context
            available_fields = (
                list(self._row_to_dict(row).keys()) if hasattr(row, "_mapping") else "unknown"
            )
            expected_fields = (
                list(model_class.model_fields.keys())
                if hasattr(model_class, "model_fields")
                else "unknown"
            )

            raise MappingError(
                f"Failed to map row to {model_class.__name__}: {e}\n"
                f"Available fields: {available_fields}\n"
                f"Expected fields: {expected_fields}"
            ) from e

    def _apply_field_mapping(self, row_dict: dict) -> dict:
        """Apply field name mapping (optimized - reuse dict if no changes)."""
        if not self._field_mapping:
            return row_dict

        # Check if any mapping is needed
        needs_mapping = any(key in self._field_mapping for key in row_dict)
        if not needs_mapping:
            return row_dict  # No changes needed, return original

        # Apply mapping
        result = {}
        for key, value in row_dict.items():
            new_key = self._field_mapping.get(key, key)
            result[new_key] = value
        return result

    def _detect_nested_columns(self, columns: list[str]) -> dict[str, list[str]]:
        """
        Detect nested columns using __ convention (optimized).

        Args:
            columns: List of column names

        Returns:
            Dict mapping parent paths to field lists
            {'profile': ['bio', 'avatar'], 'address': ['city']}
        """
        nested = {}
        for col in columns:
            if "__" in col:
                # Use rpartition for single split (faster than split)
                parent_path, _, field_name = col.rpartition("__")
                nested.setdefault(parent_path, []).append(field_name)
        return nested

    @staticmethod
    @lru_cache(maxsize=64)
    def _precompute_nested_structure(model_class: type, parent_path: str) -> tuple:
        """Pre-compute nested structure path and field types (cached)."""
        path_parts = parent_path.split("__")
        field_types = []
        current_model = model_class

        for part in path_parts:
            field_type = AlchemyMapper._get_field_type_cached(current_model, part)
            field_types.append((part, field_type))
            if field_type:
                current_model = field_type

        return tuple(field_types)

    def _apply_nested_mapping(
        self, row_dict: dict, explicit_nested: dict, model_class: type
    ) -> dict:
        """
        Apply nested mapping to transform flat dict to nested structure.

        Handles both __ convention and explicit nested_mapping.
        Optimized to avoid unnecessary dict copies and use pre-computed structures.
        """
        # Early return if no nested columns detected
        has_nested = any("__" in key for key in row_dict) or bool(explicit_nested)
        if not has_nested:
            return row_dict  # No nested mapping needed, return original (avoid copy)

        result = {}
        nested_data = defaultdict(dict)
        processed_keys = set()

        # Process __ convention columns (optimized with rpartition)
        for key, value in row_dict.items():
            if "__" in key:
                parent_path, _, field_name = key.rpartition("__")
                nested_data[parent_path][field_name] = value
                processed_keys.add(key)

        # Process explicit nested_mapping (optimized - pre-compute field-to-parent mapping)
        if explicit_nested:
            # Pre-compute mapping: field -> parent (single pass)
            fields_to_parent = {}
            for parent, fields in explicit_nested.items():
                for field in fields:
                    fields_to_parent[field] = parent

            # Single pass through row_dict
            for key, value in row_dict.items():
                if key in fields_to_parent:
                    parent = fields_to_parent[key]
                    nested_data[parent][key] = value
                    processed_keys.add(key)

        # Add non-nested fields to result (reuse row_dict items, avoid copy)
        for key, value in row_dict.items():
            if key not in processed_keys:
                result[key] = value

        # Convert nested dicts to model instances (use pre-computed structure)
        for parent_path, data in nested_data.items():
            field_types = self._precompute_nested_structure(model_class, parent_path)
            self._build_nested_structure_optimized(result, field_types, data)

        return result

    def _build_nested_structure_optimized(self, result: dict, field_types: tuple, data: dict):
        """Build nested structure using pre-computed field types (optimized)."""
        target = result
        for i, (part, field_type) in enumerate(field_types):
            if i == len(field_types) - 1:
                # Last part - instantiate the nested model
                if field_type:
                    target[part] = self._instantiate_model(field_type, data)
                else:
                    target[part] = data
            else:
                # Intermediate nesting
                if part not in target:
                    target[part] = {}
                target = target[part]

    def _build_nested_structure(
        self, result: dict, parent_path: str, data: dict, model_class: type
    ):
        """Build nested structure from parent path and data (uses optimized version)."""
        # Use pre-computed structure for better performance
        field_types = self._precompute_nested_structure(model_class, parent_path)
        self._build_nested_structure_optimized(result, field_types, data)

    @staticmethod
    @lru_cache(maxsize=512)
    def _get_field_type_cached(model_class: type, field_name: str) -> type | None:
        """Get the type of a field in a model (cached)."""
        try:
            # Check Pydantic v2
            if hasattr(model_class, "model_fields"):
                field = model_class.model_fields.get(field_name)
                if field:
                    return field.annotation
            # Check Pydantic v1
            elif hasattr(model_class, "__fields__"):
                field = model_class.__fields__.get(field_name)
                if field:
                    return field.outer_type_
        except (AttributeError, KeyError, TypeError):
            return None
        return None

    def _get_field_type(self, model_class: type, field_name: str) -> type | None:
        """Get the type of a field in a model."""
        return self._get_field_type_cached(model_class, field_name)

    def _instantiate_model(self, model_class: type, data: dict):
        """Instantiate a Pydantic model from dict data."""
        if not self._is_pydantic_cached(model_class):
            raise ValidationError(f"{model_class.__name__} is not a Pydantic model")
        return self._map_to_pydantic(data, model_class)

    @staticmethod
    @lru_cache(maxsize=256)
    def _is_pydantic_cached(model_class) -> bool:
        """Check if class is Pydantic BaseModel (cached)."""
        if not PYDANTIC_AVAILABLE or BaseModel is None:
            return False
        try:
            return isinstance(model_class, type) and issubclass(model_class, BaseModel)
        except TypeError:
            return False

    def _is_pydantic(self, cls) -> bool:
        """Check if class is Pydantic BaseModel."""
        return self._is_pydantic_cached(cls)

    def _map_to_pydantic(self, row_dict: dict, model_class: type):
        """Map dict to Pydantic model without validation (optimized for performance).

        Uses model_construct() instead of model_validate() to skip validation.
        This is safe for database queries where data is already validated/stored correctly.
        """
        try:
            return model_class.model_construct(**row_dict)
        except AttributeError as e:
            raise ValidationError(
                f"Pydantic model construction failed for {model_class.__name__}: {e}\n"
                "Hint: Ensure you're using Pydantic v2 with model_construct() support"
            ) from e
        except TypeError as e:
            # Likely missing/extra fields
            available_keys = set(row_dict.keys())
            expected_keys = (
                set(model_class.model_fields.keys())
                if hasattr(model_class, "model_fields")
                else set()
            )
            missing = expected_keys - available_keys
            extra = available_keys - expected_keys

            error_msg = f"Pydantic model construction failed for {model_class.__name__}: {e}"
            if missing:
                error_msg += f"\nMissing fields: {missing}"
            if extra:
                error_msg += f"\nExtra fields: {extra}"

            raise ValidationError(error_msg) from e
        except Exception as e:
            raise ValidationError(
                f"Pydantic model construction failed for {model_class.__name__}: {e}"
            ) from e

    async def _stream_impl(
        self,
        sql: str | Select | TextClause,
        params: dict[str, Any] | None = None,
        batch_size: int = 100,
    ) -> AsyncIterator:
        """
        Stream results asynchronously for memory efficiency.

        Args:
            sql: SQL query
            params: Query parameters
            batch_size: Number of rows to fetch per batch (default: 100)

        Yields:
            Single model instances (batch_size=1) or lists (batch_size>1)

        Examples:
            async for user in mapper.stream[User](sql):
                await process(user)

            # Stream in batches
            async for batch in mapper.stream[User](sql, batch_size=100):
                await process_batch(batch)
        """
        model_class, _, _ = self._extract_type_info()

        # Start timing
        start_time = time.perf_counter()

        # Log stream start (conditional logging)
        if self.logger.isEnabledFor(self.log_level):
            model_name = model_class.__name__ if model_class else "dict"
            log_msg = f"Starting stream [model={model_name}, batch_size={batch_size}]: {sql}"
            if params:
                log_msg += f"\nQuery params: {params}"
            self.logger.log(self.log_level, log_msg)

        # Execute query
        query_start = time.perf_counter()
        result = await self._execute_query(sql, params)
        query_time = time.perf_counter() - query_start

        # Optimized streaming - try to use async iteration if available
        total_rows = 0
        yielded_count = 0

        # Try async iteration first (for true streaming)
        if hasattr(result, "__aiter__"):
            # True async streaming
            if batch_size == 1:
                async for row in result:
                    total_rows += 1
                    if model_class:
                        yield self._map_row(row, model_class)
                    else:
                        yield self._row_to_dict(row)
                    yielded_count += 1
            else:
                # Batch streaming
                batch = []
                async for row in result:
                    total_rows += 1
                    if model_class:
                        batch.append(self._map_row(row, model_class))
                    else:
                        batch.append(self._row_to_dict(row))

                    if len(batch) >= batch_size:
                        yield batch
                        yielded_count += len(batch)
                        batch = []

                # Yield remaining items
                if batch:
                    yield batch
                    yielded_count += len(batch)
        else:
            # Fallback: fetch all rows, then iterate
            rows = result.all() if hasattr(result, "all") and callable(result.all) else list(result)

            total_rows = len(rows)

            if batch_size == 1:
                # Stream one row at a time
                for row in rows:
                    if model_class:
                        yield self._map_row(row, model_class)
                    else:
                        yield self._row_to_dict(row)
                    yielded_count += 1
            else:
                # Stream in batches (optimized - pre-allocate batch list)
                batch = []
                for row in rows:
                    if model_class:
                        batch.append(self._map_row(row, model_class))
                    else:
                        batch.append(self._row_to_dict(row))

                    if len(batch) >= batch_size:
                        yield batch
                        yielded_count += len(batch)
                        batch = []

                # Yield remaining items
                if batch:
                    yield batch
                    yielded_count += len(batch)

        # Log completion (conditional logging)
        total_time = time.perf_counter() - start_time
        if self.logger.isEnabledFor(self.log_level):
            self.logger.log(
                self.log_level,
                f"Stream completed: {total_rows} rows streamed, "
                f"exec={query_time:.3f}s, total={total_time:.3f}s",
            )

        # Call metrics callback if provided
        if self.metrics_callback:
            metrics = {
                "query_time": query_time,
                "total_time": total_time,
                "row_count": total_rows,
                "model": model_class.__name__ if model_class else "dict",
                "is_stream": True,
                "batch_size": batch_size,
            }
            try:
                self.metrics_callback(metrics)
            except Exception as e:
                self.logger.warning(f"Metrics callback failed: {e}")
