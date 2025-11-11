from __future__ import annotations
from typing import Any, Mapping, Optional, Dict, Sequence
from .client import SeerClient, JSON
from .utils import get_category

CATEGORY = "staging"

def get_staging_algorithm(
    client: SeerClient,
    algorithm: str,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/staging/{algorithm}
    Return information about a specific staging algorithm.

    Parameters
    ----------
    algorithm : str
        The staging algorithm to retrieve.
    """
    endpoint = algorithm
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


def get_staging_algorithm_version(
    client: SeerClient,
    algorithm: str,
    version: str,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/staging/{algorithm}/{version}
    Return information about a specific algorithm version.

    Parameters
    ----------
    algorithm : str
        The staging algorithm name.
    version : str
        The version identifier for the staging algorithm.
    """
    endpoint = f"{algorithm}/{version}"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


def get_staging_schema_by_id(
    client: SeerClient,
    algorithm: str,
    version: str,
    id: str,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/staging/{algorithm}/{version}/schema/{id}
    Return a single schema.

    Parameters
    ----------
    algorithm : str
        Staging algorithm.
    version : str
        Algorithm version.
    id : str
        Schema identifier.
    """
    endpoint = f"{algorithm}/{version}/schema/{id}"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


def get_staging_schema_glossary(
    client: SeerClient,
    algorithm: str,
    version: str,
    id: str,
    *,
    category: Optional[Sequence[str]] = None,   # GENERAL, STAGING, etc.
    whole_words_only: Optional[bool] = True,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/staging/{algorithm}/{version}/schema/{id}/glossary
    Return matching glossary keywords from the schema.
    Only STAGING and GENERAL glossary categories will be included by default.

    Parameters
    ----------
    algorithm : str
        Staging algorithm.
    version : str
        Algorithm version.
    id : str
        Schema identifier.
    category : Sequence[str], optional
        Limit search to specific glossary item categories.
    whole_words_only : bool, optional
        If True (default), only include whole-word matches.
    """
    endpoint = f"{algorithm}/{version}/schema/{id}/glossary"
    params: Dict[str, Any] = {}

    def put(p: Dict[str, Any], key: str, value: Optional[Any]) -> None:
        if value is None:
            return
        if isinstance(value, bool):
            p[key] = "true" if value else "false"
        else:
            p[key] = value

    def join_csv(values: Optional[Sequence[str]]) -> Optional[str]:
        if values is None:
            return None
        if isinstance(values, (str, bytes)):
            return values.decode() if isinstance(values, bytes) else values
        cleaned = [v for v in values if v is not None and str(v) != ""]
        return ",".join(str(v) for v in cleaned) if cleaned else None

    put(params, "category", join_csv(category))
    put(params, "wholeWordsOnly", whole_words_only)

    if passthrough:
        params.update(passthrough)

    return get_category(client, CATEGORY, endpoint, params=params)


# Helper for retrieving schema history
def get_staging_schema_history(
    client: SeerClient,
    algorithm: str,
    version: str,
    id: str,
    *,
    page: Optional[int] = 1,
    per_page: Optional[int] = 25,
    order: Optional[str] = None,  # ASC | DESC
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/staging/{algorithm}/{version}/schema/{id}/history
    Return the history of a single schema.

    Parameters
    ----------
    algorithm : str
        Staging algorithm.
    version : str
        Algorithm version.
    id : str
        Schema identifier.
    page : int, optional
        Page number of results to return (default 1).
    per_page : int, optional
        Entries per page to return (default 25).
    order : str, optional
        Sort order: ASC or DESC.
    """
    endpoint = f"{algorithm}/{version}/schema/{id}/history"
    params: Dict[str, Any] = {}
    if page is not None:
        params["page"] = page
    if per_page is not None:
        params["per_page"] = per_page
    if order is not None:
        params["order"] = order
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


# Helper for retrieving tables for a schema
def list_staging_schema_tables(
    client: SeerClient,
    algorithm: str,
    version: str,
    id: str,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/staging/{algorithm}/{version}/schema/{id}/tables
    Return a list of the tables involved in a specific schema.

    Parameters
    ----------
    algorithm : str
        Staging algorithm.
    version : str
        Algorithm version.
    id : str
        Schema identifier.
    """
    endpoint = f"{algorithm}/{version}/schema/{id}/tables"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)

def list_staging_schemas(
    client: SeerClient,
    algorithm: str,
    version: str,
    *,
    q: Optional[str] = None,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/staging/{algorithm}/{version}/schemas
    Return a list of schemas. If no query is supplied, all schemas will be returned.

    Parameters
    ----------
    algorithm : str
        Staging algorithm.
    version : str
        Algorithm version.
    q : str, optional
        Query string to filter schemas.
    """
    endpoint = f"{algorithm}/{version}/schemas"
    params: Dict[str, Any] = {}
    if q is not None:
        params["q"] = q
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


# Helper for retrieving schema history entries (all schemas)
def list_staging_schemas_history(
    client: SeerClient,
    algorithm: str,
    version: str,
    *,
    page: Optional[int] = 1,
    per_page: Optional[int] = 25,
    order: Optional[str] = None,  # ASC | DESC
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/staging/{algorithm}/{version}/schemas/history
    Return a list of schema history entries.

    Parameters
    ----------
    algorithm : str
        Staging algorithm.
    version : str
        Algorithm version.
    page : int, optional
        Page number of results to return (default 1).
    per_page : int, optional
        Entries per page to return (default 25).
    order : str, optional
        Sort order: ASC or DESC.
    """
    endpoint = f"{algorithm}/{version}/schemas/history"
    params: Dict[str, Any] = {}
    if page is not None:
        params["page"] = page
    if per_page is not None:
        params["per_page"] = per_page
    if order is not None:
        params["order"] = order
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


# Helper for retrieving a single table by algorithm, version, and table ID
def get_staging_table_by_id(
    client: SeerClient,
    algorithm: str,
    version: str,
    id: str,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/staging/{algorithm}/{version}/table/{id}
    Return a single table.

    Parameters
    ----------
    algorithm : str
        Staging algorithm.
    version : str
        Algorithm version.
    id : str
        Table identifier.
    """
    endpoint = f"{algorithm}/{version}/table/{id}"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)

def get_staging_table_glossary(
    client: SeerClient,
    algorithm: str,
    version: str,
    id: str,
    *,
    category: Optional[Sequence[str]] = None,   # GENERAL, STAGING, etc.
    whole_words_only: Optional[bool] = True,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/staging/{algorithm}/{version}/table/{id}/glossary
    Return matching glossary keywords from the table.
    Only STAGING and GENERAL glossary categories will be included by default.

    Parameters
    ----------
    algorithm : str
        Staging algorithm.
    version : str
        Algorithm version.
    id : str
        Table identifier.
    category : Sequence[str], optional
        Limit search to specific glossary item categories.
    whole_words_only : bool, optional
        If True (default), only include whole-word matches.
    """
    endpoint = f"{algorithm}/{version}/table/{id}/glossary"
    params: Dict[str, Any] = {}

    def put(p: Dict[str, Any], key: str, value: Optional[Any]) -> None:
        if value is None:
            return
        if isinstance(value, bool):
            p[key] = "true" if value else "false"
        else:
            p[key] = value

    def join_csv(values: Optional[Sequence[str]]) -> Optional[str]:
        if values is None:
            return None
        if isinstance(values, (str, bytes)):
            return values.decode() if isinstance(values, bytes) else values
        cleaned = [v for v in values if v is not None and str(v) != ""]
        return ",".join(str(v) for v in cleaned) if cleaned else None

    put(params, "category", join_csv(category))
    put(params, "wholeWordsOnly", whole_words_only)

    if passthrough:
        params.update(passthrough)

    return get_category(client, CATEGORY, endpoint, params=params)


# Helper for retrieving table history
def get_staging_table_history(
    client: SeerClient,
    algorithm: str,
    version: str,
    id: str,
    *,
    page: Optional[int] = 1,
    per_page: Optional[int] = 25,
    order: Optional[str] = None,  # ASC | DESC
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/staging/{algorithm}/{version}/table/{id}/history
    Return the history of a single table.

    Parameters
    ----------
    algorithm : str
        Staging algorithm.
    version : str
        Algorithm version.
    id : str
        Table identifier.
    page : int, optional
        Page number of results to return (default 1).
    per_page : int, optional
        Entries per page to return (default 25).
    order : str, optional
        Sort order: ASC or DESC.
    """
    endpoint = f"{algorithm}/{version}/table/{id}/history"
    params: Dict[str, Any] = {}
    if page is not None:
        params["page"] = page
    if per_page is not None:
        params["per_page"] = per_page
    if order is not None:
        params["order"] = order
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


# Helper for retrieving schemas that use a specific table
def list_staging_table_schemas(
    client: SeerClient,
    algorithm: str,
    version: str,
    id: str,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/staging/{algorithm}/{version}/table/{id}/schemas
    Return a list of the schemas which use a specific table.

    Parameters
    ----------
    algorithm : str
        Staging algorithm.
    version : str
        Algorithm version.
    id : str
        Table identifier.
    """
    endpoint = f"{algorithm}/{version}/table/{id}/schemas"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


# Helper for retrieving a list of matching tables (only name and title)
def list_staging_tables(
    client: SeerClient,
    algorithm: str,
    version: str,
    *,
    q: Optional[str] = None,
    unused: Optional[bool] = None,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/staging/{algorithm}/{version}/tables
    Return a list of matching tables. Only the name and title are included in the results.

    Parameters
    ----------
    algorithm : str
        Staging algorithm.
    version : str
        Algorithm version.
    q : str, optional
        Query string to filter results.
    unused : bool, optional
        If True, limit to tables not used in any schema.
    """
    endpoint = f"{algorithm}/{version}/tables"
    params: Dict[str, Any] = {}
    if q is not None:
        params["q"] = q
    if unused is not None:
        params["unused"] = "true" if unused else "false"
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)

def list_staging_tables_history(
    client: SeerClient,
    algorithm: str,
    version: str,
    *,
    page: Optional[int] = 1,
    per_page: Optional[int] = 25,
    order: Optional[str] = None,  # ASC | DESC
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/staging/{algorithm}/{version}/tables/history
    Return a list of table history entries.

    Parameters
    ----------
    algorithm : str
        Staging algorithm.
    version : str
        Algorithm version.
    page : int, optional
        Page number of results to return (default 1).
    per_page : int, optional
        Entries per page to return (default 25).
    order : str, optional
        Sort order: ASC or DESC.
    """
    endpoint = f"{algorithm}/{version}/tables/history"
    params: Dict[str, Any] = {}
    if page is not None:
        params["page"] = page
    if per_page is not None:
        params["per_page"] = per_page
    if order is not None:
        params["order"] = order
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


# Helper for retrieving all supported versions of an algorithm
def list_staging_algorithm_versions(
    client: SeerClient,
    algorithm: str,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/staging/{algorithm}/versions
    Return information about all the supported versions of an algorithm.

    Parameters
    ----------
    algorithm : str
        Staging algorithm.
    """
    endpoint = f"{algorithm}/versions"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)


# Helper for retrieving all staging algorithms
def list_staging_algorithms(
    client: SeerClient,
    *,
    passthrough: Optional[Mapping[str, Any]] = None,
) -> JSON:
    """
    GET /rest/staging/algorithms
    Return a list of all staging algorithms.
    """
    endpoint = "algorithms"
    params: Dict[str, Any] = {}
    if passthrough:
        params.update(passthrough)
    return get_category(client, CATEGORY, endpoint, params=params)