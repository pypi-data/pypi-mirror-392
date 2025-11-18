"""
Cross-service cache invalidation registry.

This module handles registration and execution of cross-service cache invalidation.
It provides shared utilities used by both BaseCacheRule (for local invalidation)
and cross-service invalidation handlers.
"""

import json
from sqlalchemy import event, inspect


# Global registry for cross-service invalidation rules
# Format: {model_path: [rule_config1, rule_config2, ...]}
_cross_service_registry = {}
_cross_service_listeners_registered = set()


def extract_invalidation_params(target, invalidation_key_fields, key_mapping):
    """
    Extract invalidation parameters from a changed model instance.
    
    This is a shared utility used by both:
    - BaseCacheRule._extract_invalidation_params() for local invalidation
    - Cross-service invalidation handler for remote invalidation
    
    Args:
        target: SQLAlchemy model instance that triggered the event
        invalidation_key_fields: List of API parameter names (e.g., ["customer_id"])
        key_mapping: Dict mapping DB columns to API params (e.g., {"party_id": "customer_id"})
    
    Returns:
        dict: Parameters for cache invalidation (e.g., {"customer_id": 123})
    
    Examples:
        # Without key_mapping (DB column = API param)
        invalidation_key_fields = ["customer_id", "country_code"]
        key_mapping = {}
        target.customer_id = 123, target.country_code = "sa"
        Returns: {"customer_id": 123, "country_code": "sa"}
        
        # With key_mapping (DB column → API param)
        invalidation_key_fields = ["customer_id"]
        key_mapping = {"party_id": "customer_id"}
        target.party_id = 123
        Returns: {"customer_id": 123}
    """
    params = {}
    
    for api_param in invalidation_key_fields:
        # Find DB column name from key_mapping
        db_column = None
        for db_col, mapped_api_param in key_mapping.items():
            if mapped_api_param == api_param:
                db_column = db_col
                break
        
        # If no mapping found, assume db_column = api_param
        if db_column is None:
            db_column = api_param
        
        # Extract value from target model
        if hasattr(target, db_column):
            params[api_param] = getattr(target, db_column)
        else:
            print(
                f"[Cache WARNING] Field '{db_column}' not found on {target.__class__.__name__}. "
                f"Check key_mapping in invalidation configuration."
            )
    
    return params


def format_value_for_cache_key(value):
    """
    Format a value for use in cache keys.
    
    Shared utility for consistent value formatting across local and cross-service invalidation.
    
    Args:
        value: The value to format (int, str, bool, dict, list, etc.)
    
    Returns:
        str: Formatted value suitable for cache key
    """
    if isinstance(value, (int, str)):
        return str(value)
    else:
        return json.dumps(value)


def build_cache_key_pattern(service_name, api_path, invalidation_params):
    """
    Build a cache key pattern for invalidation.
    
    Shared utility to ensure consistent pattern building.
    
    Args:
        service_name: Service name (e.g., "thrivve-service")
        api_path: API path (e.g., "/finance/api/v1/me/balance")
        invalidation_params: Parameters for granular invalidation (e.g., {"customer_id": 123})
    
    Returns:
        str: Cache key pattern for Redis SCAN
    
    Examples:
        build_cache_key_pattern("thrivve-service", "/api/balance", {"customer_id": 123})
        Returns: "thrivve-service:/api/balance:customer_id=123:*"
        
        build_cache_key_pattern("thrivve-service", "/api/balance", {})
        Returns: "thrivve-service:/api/balance:*"
    """
    if invalidation_params:
        tags = []
        for api_param, value in invalidation_params.items():
            formatted_value = format_value_for_cache_key(value)
            tags.append(f"{api_param}={formatted_value}")
        
        tag_str = ":".join(tags)
        return f"{service_name}:{api_path}:{tag_str}:*"
    else:
        # Path-based invalidation (all keys for this endpoint)
        return f"{service_name}:{api_path}:*"


def invalidate_cache_by_pattern(redis_client, pattern):
    """
    Invalidate cache entries matching a pattern.
    
    Shared utility for cache invalidation via Redis SCAN.
    
    Args:
        redis_client: Redis/Valkey client instance
        pattern: Redis key pattern (e.g., "service:/path:customer_id=123:*")
    
    Returns:
        int: Number of keys deleted
    """
    if not redis_client:
        print("[Cache WARNING] Redis client not available for invalidation")
        return 0
    
    try:
        deleted = 0
        for key in redis_client.scan_iter(pattern):
            redis_client.delete(key)
            deleted += 1
        
        if deleted > 0:
            print(f"[Cache] Invalidated {deleted} key(s) matching pattern: {pattern}")
        
        return deleted
        
    except Exception as e:
        print(f"[Cache WARNING] Cache invalidation failed for pattern {pattern}: {e}")
        return 0


def _model_exists(model_path):
    """
    Check if a model path exists before attempting to import.

    This allows graceful degradation when cache metadata references models
    that don't exist in the current service.

    Args:
        model_path: Full model path (e.g., "app.models.core.Customer")

    Returns:
        bool: True if model can be imported, False otherwise
    """
    import importlib

    try:
        module_path, class_name = model_path.rsplit(".", 1)
        module = importlib.import_module(module_path)
        return hasattr(module, class_name)
    except (ImportError, ValueError, AttributeError):
        return False


def register_cross_service_invalidation_batch(
    source_service,
    api_path,
    invalidation_key_fields,
    models
):
    """
    Register cross-service cache invalidation for multiple models.
    Called automatically when MicroFetcher receives cache metadata.

    Args:
        source_service: Service that owns the cache (e.g., "thrivve-service")
        api_path: API path to invalidate (e.g., "/finance/api/v1/me/balance")
        invalidation_key_fields: Fields for granular invalidation (e.g., ["customer_id"])
        models: Dict of model paths and their configurations (SIMPLIFIED - no service wrapper)

    Example models structure (SIMPLIFIED):
        {
            "app.models.core.Customer": {
                "events": ["after_update"],
                "key_mapping": {"id": "customer_id"}
            },
            "app.models.settings.WalletSettings": {
                "events": ["after_update", "after_insert"],
                "key_mapping": {"customer_id": "customer_id"}
            }
        }

    Returns:
        int: Number of models successfully registered
    """
    import importlib

    registered_count = 0
    skipped_count = 0

    for model_path, config in models.items():
        # Check if model exists before importing
        if not _model_exists(model_path):
            print(f"[Cache] Skipping cross-service registration: Model '{model_path}' not found in this service")
            skipped_count += 1
            continue

        try:
            # Import the model class
            module_path, class_name = model_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            model_class = getattr(module, class_name)
            
            events = config.get("events", [])
            key_mapping = config.get("key_mapping", {})
            columns = config.get("columns", [])
            
            # Add to registry
            if model_path not in _cross_service_registry:
                _cross_service_registry[model_path] = []
            
            # Check if already registered (avoid duplicates)
            existing = [
                r for r in _cross_service_registry[model_path]
                if r["source_service"] == source_service and r["api_path"] == api_path
            ]
            
            if existing:
                print(f"[Cache] Cross-service rule already registered: {source_service}:{api_path} → {model_path}")
                continue
            
            # Add new rule
            _cross_service_registry[model_path].append({
                "source_service": source_service,
                "api_path": api_path,
                "invalidation_key_fields": invalidation_key_fields,
                "key_mapping": key_mapping,
                "events": events,
                "columns": columns
            })
            
            # Register SQLAlchemy listener (once per model+events)
            registry_key = (model_class, tuple(events))
            if registry_key not in _cross_service_listeners_registered:
                for ev in events:
                    event.listen(model_class, ev, _cross_service_invalidation_handler)
                
                _cross_service_listeners_registered.add(registry_key)
                print(f"[Cache] Registered cross-service listener: {model_path} → {events}")
            
            registered_count += 1

        except Exception as e:
            print(f"[Cache WARNING] Failed to register cross-service invalidation for {model_path}: {e}")
            skipped_count += 1
            continue

    if registered_count > 0:
        print(f"[Cache] Registered {registered_count} cross-service invalidation rule(s) for {source_service}:{api_path}")
    if skipped_count > 0:
        print(f"[Cache] Skipped {skipped_count} model(s) not present in this service")

    return registered_count


def _cross_service_invalidation_handler(mapper, connection, target):
    """
    Global handler for cross-service cache invalidation.
    Triggered when a model registered for cross-service invalidation changes.
    
    Args:
        mapper: SQLAlchemy mapper
        connection: Database connection
        target: Model instance that triggered the event
    """
    model_path = f"{target.__class__.__module__}.{target.__class__.__name__}"
    
    if model_path not in _cross_service_registry:
        return
    
    # Get all cache rules registered for this model
    for rule_config in _cross_service_registry[model_path]:
        source_service = rule_config["source_service"]
        api_path = rule_config["api_path"]
        invalidation_key_fields = rule_config["invalidation_key_fields"]
        key_mapping = rule_config["key_mapping"]
        watched_cols = rule_config.get("columns", [])
        
        # Check if watched columns changed (if specified)
        if watched_cols:
            state = inspect(target)
            changed = [
                attr.key
                for attr in state.attrs
                if attr.key in watched_cols and attr.history.has_changes()
            ]
            if not changed:
                continue  # No watched columns changed, skip invalidation
        
        # Extract invalidation parameters from the changed model
        invalidation_params = extract_invalidation_params(
            target=target,
            invalidation_key_fields=invalidation_key_fields,
            key_mapping=key_mapping
        )
        
        # Invalidate cache in the source service
        _invalidate_remote_cache(
            source_service=source_service,
            api_path=api_path,
            invalidation_params=invalidation_params
        )


def _invalidate_remote_cache(source_service, api_path, invalidation_params):
    """
    Invalidate cache in remote service by directly accessing Valkey.
    
    Since all services share the same Valkey instance, we can directly
    delete cache keys without making HTTP requests.
    
    Args:
        source_service: Service name that owns the cache (e.g., "thrivve-service")
        api_path: API path to invalidate (e.g., "/finance/api/v1/me/balance")
        invalidation_params: Parameters for granular invalidation (e.g., {"customer_id": 123})
    """
    # Import here to avoid circular dependency
    from wedeliver_core_plus.helpers.caching.valkey_redis_utils import BaseCacheRule
    
    if not BaseCacheRule._redis_client:
        print("[Cache WARNING] Redis client not available for cross-service invalidation")
        return
    
    # Build cache key pattern
    pattern = build_cache_key_pattern(source_service, api_path, invalidation_params)
    
    # Invalidate using shared utility
    deleted = invalidate_cache_by_pattern(BaseCacheRule._redis_client, pattern)
    
    if deleted > 0:
        print(f"[Cache] Cross-service invalidation: Deleted {deleted} key(s) for {source_service}:{api_path}")


def get_cross_service_registry():
    """
    Get the current cross-service registry for debugging/monitoring.
    
    Returns:
        dict: Current registry state with registry and listener count
    """
    return {
        "registry": _cross_service_registry,
        "listeners_count": len(_cross_service_listeners_registered),
        "registered_models": list(_cross_service_registry.keys())
    }

