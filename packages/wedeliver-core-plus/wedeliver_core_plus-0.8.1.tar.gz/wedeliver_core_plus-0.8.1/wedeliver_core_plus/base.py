class WedeliverCorePlus:
    """
    Singleton class for WedeliverCorePlus
    """
    __app = None

    @staticmethod
    def get_app():
        """ Static access method. """
        if WedeliverCorePlus.__app is None:
            WedeliverCorePlus()
        return WedeliverCorePlus.__app

    def __init__(self, app=None):
        """ Virtually private constructor. """
        if WedeliverCorePlus.__app is not None:
            raise Exception("This class is a singleton!")
        else:
            WedeliverCorePlus.__app = app
            _setup_default_routes(app)
            _setup_babel_locale(app)


def _setup_babel_locale(app):
    if 'babel' not in app.extensions:
        return

    from flask import request
    from wedeliver_core_plus.helpers.auth import Auth
    babel = app.extensions['babel']

    @babel.localeselector
    def get_locale():
        """
        This function is used to determine the language to use for translations.
        """
        # if a user is logged in, use the locale from the user settings
        user = Auth.get_user()

        language = user.get('language')
        if language:
            return language
        # otherwise try to guess the language from the user accept
        # header the browser transmits. The best match wins.
        return request.accept_languages.best_match(['ar', 'en'])


def _process_cache_registration_metadata(metadata_list):
    """
    Process cache registration metadata from upstream services.

    1. Store metadata in Flask g object for downstream MicroFetcher calls (chaining)
    2. Register cross-service invalidation listeners for models in THIS service

    Args:
        metadata_list: List of cache metadata dictionaries from upstream services
    """
    from flask import g
    from wedeliver_core_plus.helpers.caching.cache_invalidation_registry import register_cross_service_invalidation_batch

    # Store in g object for downstream calls (chaining)
    if not hasattr(g, '_cache_registration_metadata'):
        g._cache_registration_metadata = []
    g._cache_registration_metadata.extend(metadata_list)

    # Register invalidation listeners for models in THIS service
    for metadata in metadata_list:
        cross_service_map = metadata.get("cross_service_map", {})

        # cross_service_map now contains models directly (no service name wrapper)
        if cross_service_map:
            register_cross_service_invalidation_batch(
                source_service=metadata["source_service"],
                api_path=metadata["api_path"],
                invalidation_key_fields=metadata["invalidation_key_fields"],
                models=cross_service_map  # Direct pass - models are at top level
            )


def _setup_default_routes(app):
    from wedeliver_core_plus.app_decorators.app_entry import route
    from wedeliver_core_plus.helpers.fetch_relational_data import fetch_relational_data
    @route(
        path='/',
        require_auth=False
    )
    def _health_check_service():
        return dict(name="{} Service".format(app.config.get('SERVICE_NAME')), works=True)

    @route(
        path='/health_check',
        require_auth=False
    )
    def _health_check_with_path_service():
        return dict(name="{} Service".format(app.config.get('SERVICE_NAME')), works=True)

    @route("/fetch_relational_data", methods=["POST"], require_auth=False)
    def _fetch_relational_data_service(validated_data):
        """
        Receives MicroFetcher requests and processes cache registration metadata.
        """
        # Extract and process cache metadata
        cache_metadata_key = '__cache_registration_metadata__'
        if validated_data.get(cache_metadata_key):
            _process_cache_registration_metadata(validated_data.get(cache_metadata_key))

        # Extract user auth data
        user_data_key = '__user_auth_data__'
        if validated_data.get(user_data_key) is not None:
            from wedeliver_core_plus.helpers.auth import Auth
            Auth.set_user(validated_data.get(user_data_key))

        # Clean up metadata from validated_data
        validated_data.pop(cache_metadata_key, None)
        validated_data.pop(user_data_key, None)

        return fetch_relational_data(**validated_data)
