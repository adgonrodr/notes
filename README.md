def get_config_environments_by_key(...):
    """Return a config value by key with precedence: env var → env section → global.

    This helper fetches a configuration value following a clear precedence order:
    1) If an environment variable matching the pattern
       ``{env_var_prefix}_{env}_{key}`` is set, its value is returned.
    2) Otherwise, it looks up ``config[env][key]``.
    3) If still not found, it falls back to ``config["global"][key]``.

    The environment-variable name is typically uppercased. If your keys or env
    names include characters outside ``[A-Za-z0-9_]``, consider normalizing them
    (e.g., replace non-alphanumerics with underscores) to form a valid variable
    name.

    Args:
      key: Logical key to retrieve from the configuration (e.g., ``"API_URL"``).
      env: Active environment name (e.g., ``"dev"``, ``"prod"``) used for the
        second lookup step and for composing the environment-variable name.
      config: Nested configuration mapping expected to contain both an
        environment section (e.g., ``config[env]``) and a global section
        (``config["global"]``).
      env_var_prefix: Prefix used when composing the environment-variable name.
        The full pattern is ``{env_var_prefix}_{env}_{key}``.

    Returns:
      The resolved configuration value.

    Raises:
      KeyError: If the value cannot be resolved from the environment variable,
        the provided environment section, or the global section.
      ValueError: If ``env`` is empty/invalid or ``config`` lacks the required
        sections (e.g., missing ``"global"``).

    Examples:
      Resolve from environment variable first:

      >>> import os
      >>> os.environ["APP_DEV_API_URL"] = "https://env.example"
      >>> cfg = {"dev": {"API_URL": "https://dev.example"}, "global": {"API_URL": "https://global.example"}}
      >>> get_config_environments_by_key("API_URL", env="dev", config=cfg, env_var_prefix="APP")
      'https://env.example'

      Fallback to environment section when the env var is not set:

      >>> os.environ.pop("APP_DEV_API_URL", None)
      >>> get_config_environments_by_key("API_URL", env="dev", config=cfg, env_var_prefix="APP")
      'https://dev.example'

      Fallback to global section if the key is missing in the environment:

      >>> cfg = {"dev": {}, "global": {"API_URL": "https://global.example"}}
      >>> get_config_environments_by_key("API_URL", env="dev", config=cfg, env_var_prefix="APP")
      'https://global.example'
    """
    ...

def get_config_by_key(...):
    """Return a config value by key with precedence: env var → config file.

    This helper fetches a configuration value following a simple precedence:
    1) If an environment variable matching the pattern
       ``{env_var_prefix}_{key}`` is set, its value is returned.
    2) Otherwise, it looks up ``config[key]``.
    If neither is found, a ``KeyError`` is raised.

    The environment-variable name is typically uppercased. If your key includes
    characters outside ``[A-Za-z0-9_]`` (e.g., hyphens or dots), consider
    normalizing it (e.g., replace non-alphanumerics with underscores) when
    building the environment-variable name.

    Args:
      key: Logical key to retrieve from the configuration (e.g., ``"API_URL"``).
      config: Flat (or pre-resolved) configuration mapping containing the key
        (e.g., ``{"API_URL": "https://example"} ``).
      env_var_prefix: Prefix used when composing the environment-variable name.
        The full pattern is ``{env_var_prefix}_{key}``.

    Returns:
      The resolved configuration value.

    Raises:
      KeyError: If the value cannot be resolved from either the environment
        variable or the config mapping.
      ValueError: If ``key`` is empty/invalid or ``config`` is not a mapping.

    Examples:
      Resolve from environment variable first:

      >>> import os
      >>> os.environ["APP_API_URL"] = "https://env.example"
      >>> cfg = {"API_URL": "https://conf.example"}
      >>> get_config_by_key("API_URL", config=cfg, env_var_prefix="APP")
      'https://env.example'

      Fallback to config value when the env var is not set:

      >>> os.environ.pop("APP_API_URL", None)
      >>> get_config_by_key("API_URL", config=cfg, env_var_prefix="APP")
      'https://conf.example'

      Raise if neither env var nor config contains the key:

      >>> cfg = {}
      >>> get_config_by_key("API_URL", config=cfg, env_var_prefix="APP")
      Traceback (most recent call last):
      ...
      KeyError: 'API_URL'
    """
    ...