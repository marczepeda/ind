# Run with:
#   CLINICALTRIALS_LIVE=1 pytest -q tests/clinical_trials/endpoints.py
#
# Notes:
# - These are **smoke** tests: they assert "no exception + sane JSON shape".
# - Assertions are intentionally loose to avoid flakiness when the API evolves.

from __future__ import annotations

import os
import typing as t
import pytest

from ind.clinical_trials import (
    ClinicalTrialsClient,
    ClinicalTrialsError,
    # studies
    list_studies,
    get_study,
    get_studies_metadata,
    get_search_areas,
    get_enums,
    # stats
    get_study_sizes,
    get_field_values,
    get_field_sizes,
    # version
    get_version,
)

LIVE = os.getenv("CLINICALTRIALS_LIVE") == "1"

pytestmark = pytest.mark.skipif(
    not LIVE, reason="Set CLINICALTRIALS_LIVE=1 to run ClinicalTrials.gov smoke tests."
)

# A gentle rate limit to avoid being noisy.
CLIENT = ClinicalTrialsClient(timeout=20.0, rate_limit_per_sec=2.0)


def _is_dict(obj: t.Any) -> bool:
    return isinstance(obj, dict)


def _pluck_nct_id(study: dict) -> t.Optional[str]:
    """
    Try to pull an NCT ID out of a study record. The API nests it under:
      protocolSection.identificationModule.nctId
    If the shape changes, return None (test remains a smoke test).
    """
    try:
        return study["protocolSection"]["identificationModule"]["nctId"]
    except Exception:
        return None


def test_version() -> None:
    res = get_version(CLIENT)
    assert _is_dict(res) or isinstance(res, list)
    assert bool(res)  # not empty


def test_studies_list_and_single() -> None:
    # Use query.cond to likely get at least one result.
    res = list_studies(
        CLIENT,
        query_cond="cancer",
        page_size=1,
        fields=["NCTId", "BriefTitle", "OverallStatus"],
        count_total=False,
    )
    assert _is_dict(res)
    studies = res.get("studies", [])
    assert isinstance(studies, list)
    if studies:
        nct_id = _pluck_nct_id(studies[0])
        if nct_id:
            detail = get_study(CLIENT, nct_id)
            assert isinstance(detail, dict)
            assert len(detail) > 0


def test_metadata_enums_search_areas() -> None:
    meta = get_studies_metadata(CLIENT)
    enums = get_enums(CLIENT)
    areas = get_search_areas(CLIENT)
    for obj in (meta, enums, areas):
        assert isinstance(obj, (dict, list))
        assert bool(obj)


def test_stats_size() -> None:
    res = get_study_sizes(CLIENT)
    assert isinstance(res, dict)
    # Expect keys per spec, but don't be strict about all
    assert "totalStudies" in res
    assert "averageSizeBytes" in res


def test_stats_field_values() -> None:
    # OverallStatus is a well-known enum (e.g., Recruiting, Completed, etc.)
    res = get_field_values(CLIENT, fields=["OverallStatus"], types=["ENUM"])
    assert isinstance(res, list)
    if res:
        first = res[0]
        assert isinstance(first, dict)
        # Common keys
        assert "field" in first
        assert "topValues" in first


def test_stats_field_sizes() -> None:
    # Ask for sizes of a nested field
    res = get_field_sizes(CLIENT, fields=["protocolSection.armsInterventionsModule.armGroups.interventionNames"])
    assert isinstance(res, list)
    if res:
        first = res[0]
        assert isinstance(first, dict)
        # Common keys
        assert "minSize" in first
        assert "maxSize" in first