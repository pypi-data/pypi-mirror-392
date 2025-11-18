import ast
import json
from functools import wraps

from sqlalchemy.orm.base import object_mapper
import flask_sqlalchemy
from flask import request, g
from marshmallow import ValidationError
from sqlalchemy.orm.exc import UnmappedInstanceError

from wedeliver_core_plus.helpers.exceptions import AppValidationError


def is_mapped(obj):
    try:
        data = obj
        if isinstance(data, list) and len(data):
            data = obj[0]
        object_mapper(data)
    except UnmappedInstanceError:
        return False
    return True

def is_result_row(obj):
    try:
        data = obj
        if isinstance(data, list) and len(data):
            data = obj[0]

        if hasattr(data, '__row_data__'):
            return True
    except UnmappedInstanceError:
        return False
    return False


def _serialize_result(result, schema, many):
    """
    Serialize the result from a route handler function.

    Handles three types of results:
    1. Pagination objects - extracts items and metadata
    2. Mapped SQLAlchemy models - uses schema to dump
    3. Raw data (dict/list) - returns as-is

    Args:
        result: The raw result from the route handler
        schema: Marshmallow schema class for serialization
        many: Boolean flag for list serialization

    Returns:
        Serialized output (dict or list)
    """
    if isinstance(result, flask_sqlalchemy.Pagination):
        items = schema(many=isinstance(result.items, list)).dump(result.items)
        output = dict(
            items=items,
            total=result.total,
            next_num=result.next_num,
            prev_num=result.prev_num,
            page=result.page,
            per_page=result.per_page
        )
    elif is_mapped(result) or is_result_row(result):  # is model instance
        output = schema(many=isinstance(result, list)).dump(result)
    else:
        output = result

    return output


def _store_cache_metadata_in_context(service_name, api_path, invalidation_key_fields, cross_service_map):
    """
    Store cache metadata in Flask request context (g object).
    This allows MicroFetcher to access it and piggyback registration data.

    Args:
        service_name: Current service name (e.g., "thrivve-service")
        api_path: API path (e.g., "/finance/api/v1/me/balance")
        invalidation_key_fields: Fields for granular invalidation (e.g., ["customer_id"])
        cross_service_map: Cross-service invalidation configuration
    """
    if not hasattr(g, '_cache_registration_metadata'):
        g._cache_registration_metadata = []

    g._cache_registration_metadata.append({
        "source_service": service_name,
        "api_path": api_path,
        "invalidation_key_fields": invalidation_key_fields,
        "cross_service_map": cross_service_map
    })


def serializer(path, schema=None, many=False, cache_rule=None):
    def factory(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            # user_language = Auth.get_user_language()
            # with force_locale(user_language):
            is_function_with_validated_data = False
            if hasattr(func, '__wrapped__'):
                old_vars = func.__wrapped__.__code__.co_varnames
                is_function_with_validated_data = old_vars.__contains__('validated_data')

            appended_kws = kwargs.pop('appended_kws', None)

            try:
                client_data = dict()

                if kwargs:
                    client_data.update(**kwargs)

                content_type = request.headers.get('Content-Type')
                if content_type and 'application/json' in content_type:
                    # if the request have json payload, the user need to send the Content-Type as application/json
                    try:
                        client_data.update(request.json)
                    except Exception:
                        pass

                elif request.form:
                    client_data.update(request.form.to_dict())

                    def _sanitize(cd):
                        for _k in cd.keys():
                            try:
                                value = ast.literal_eval(cd[_k])
                                if isinstance(value, int):
                                    value = str(value)
                                cd[_k] = value
                            except Exception:
                                try:
                                    value = json.loads(cd[_k])
                                    if isinstance(value, list):
                                        output = []
                                        for _v in value:
                                            output.append(_sanitize(_v))
                                        cd[_k] = output
                                    if isinstance(value, dict):
                                        cd[_k] = _sanitize(value)
                                except Exception:
                                    pass
                        return cd

                    _sanitize(client_data)

                if request.args:
                    client_data.update(request.args.to_dict())

                inputs = client_data  # .to_dict()
                if appended_kws:
                    inputs.update(appended_kws)

                if schema:
                    result = schema(many=many).load(inputs)
                else:
                    result = inputs
            except ValidationError as e:
                raise AppValidationError(e.messages)

            if result:
                if is_function_with_validated_data:
                    kwargs.update(dict(validated_data=result))
            # if schema and request.method == "GET":

            # ---------------- Cache logic BEFORE function call ----------------
            cache_instance = None
            cache_key = None
            if cache_rule:
                request_data = kwargs.get("validated_data", {})
                # Initialize the rule (it may auto-register SQLAlchemy listeners)
                # Pass path into the cache rule instance
                cache_instance = cache_rule(path)

                # Store cache metadata in Flask g for MicroFetcher to piggyback
                if hasattr(cache_instance, 'cross_service_invalidation_map') and cache_instance.cross_service_invalidation_map:
                    from wedeliver_core_plus.helpers.caching.valkey_redis_utils import BaseCacheRule
                    _store_cache_metadata_in_context(
                        service_name=BaseCacheRule._service_name,
                        api_path=path,
                        invalidation_key_fields=cache_instance.invalidation_key_fields,
                        cross_service_map=cache_instance.cross_service_invalidation_map
                    )

                # Use path + request args/body as key
                cache_key = cache_instance.make_key(request_data)
                cached_data = cache_instance.get(cache_key)
                if cached_data is not None:
                    print(f"[Cache] HIT for {path}")

                    # ---------------- Cache Validation (if enabled) ----------------
                    from flask import current_app
                    validation_mode = current_app.config.get('CACHE_VALIDATION_MODE', 'off')

                    if validation_mode != 'off' and cache_instance._should_validate(validation_mode):
                        # Validate cache by calling the route handler function
                        # This runs the same business logic to get fresh data
                        cache_instance._validate_cache_data(
                            cache_key=cache_key,
                            cached_data=cached_data,
                            route_handler_func=func,  # The route handler function
                            validated_data=request_data,
                            schema=schema,  # Pass schema for serialization
                            many=many  # Pass many flag for serialization
                        )

                    # Add is_cached flag if response is dict or list
                    if isinstance(cached_data, dict):
                        cached_data["is_cached"] = True
                    elif isinstance(cached_data, list):
                        # Loop through list and add is_cached to each dict element
                        for item in cached_data:
                            if isinstance(item, dict):
                                item["is_cached"] = True

                    return cached_data  # 🟢 return from cache immediately

            # ---------------- Execute main function ----------------

            try:
                result = func(*args, **kwargs)
                output = _serialize_result(result, schema, many)
            except ValidationError as e:
                raise AppValidationError(e.messages)

            # ---------------- Cache AFTER execution ----------------
            if cache_instance and cache_key and output is not None:
                cache_instance.set(cache_key, output)

            return output

            # return func(*args, **kwargs)

        return decorator

    return factory
