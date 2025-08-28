def get_one_result(...):
    """Return a single result dict from a Collibra-style response.

    Expects a Collibra response payload containing a ``"results"`` list.
    Behavior:
      - If ``results`` is empty, returns ``None``.
      - If ``results`` has exactly one element, returns that element (as ``dict``).
      - If ``results`` has more than one element, raises ``CustomException``.

    Args:
      response: Mapping returned by the Collibra API. Must include a ``"results"`` key
        with a list value.
      results_key: Optional key name for the results list if your response uses a
        different field name. Defaults to ``"results"``.

    Returns:
      dict | None: The single result object if present, otherwise ``None``.

    Raises:
      CustomException: If more than one result is present.
      ValueError: If the response does not contain ``results_key`` or if it is not a list.
      TypeError: If any item inside the results list is not a mapping/dict.

    Examples:
      One result:

      >>> payload = {"results": [{"id": "123", "name": "Asset A"}]}
      >>> get_one_result(payload)
      {'id': '123', 'name': 'Asset A'}

      No results:

      >>> payload = {"results": []}
      >>> get_one_result(payload) is None
      True

      Multiple results (raises):

      >>> payload = {"results": [{"id": "1"}, {"id": "2"}]}
      >>> get_one_result(payload)
      Traceback (most recent call last):
      ...
      CustomException: Expected 0 or 1 result, got 2.
    """
    ...

def get_many_result(...):
    """Return the list of result dicts from a Collibra-style response.

    Expects a Collibra response payload containing a ``"results"`` list.
    Behavior:
      - If the response contains ``results`` (even if empty), returns that list.
      - If the response **does not** contain ``results`` (missing or wrong type),
        raises ``CustomException``.

    Args:
      response: Mapping returned by the Collibra API. Must include a ``"results"`` key
        with a list value.
      results_key: Optional key name for the results list if your response uses a
        different field name. Defaults to ``"results"``.

    Returns:
      list[dict]: The list of result objects (may be empty).

    Raises:
      CustomException: If the response does not contain ``results_key`` or if it is not a list.
      TypeError: If any item inside the results list is not a mapping/dict.

    Examples:
      Many (or some) results:

      >>> payload = {"results": [{"id": "1"}, {"id": "2"}]}
      >>> get_many_result(payload)
      [{'id': '1'}, {'id': '2'}]

      Empty results (valid, returns empty list):

      >>> payload = {"results": []}
      >>> get_many_result(payload)
      []

      Missing results (raises):

      >>> payload = {"data": []}
      >>> get_many_result(payload)
      Traceback (most recent call last):
      ...
      CustomException: Response does not contain a valid 'results' list.
    """
    ...