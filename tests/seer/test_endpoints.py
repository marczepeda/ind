import pytest

# We will monkeypatch each module's get_category to capture calls

def _install_spy(monkeypatch, module):
    calls = []
    def _spy(client, category, endpoint, params=None):
        calls.append((category, endpoint, dict(params or {})))
        # return a simple echo to validate return path
        return {"category": category, "endpoint": endpoint, "params": dict(params or {})}
    monkeypatch.setattr(module, "get_category", _spy, raising=True)
    return calls

class DummyClient:
    pass

# -------------------- GLOSSARY --------------------
from ind.seer import glossary as seer_glossary

def test_glossary_list(monkeypatch):
    calls = _install_spy(monkeypatch, seer_glossary)
    seer_glossary.list_glossary(
        DummyClient(), "2025",
        q="lymph", category=["GENERAL", "STAGING"], count=50, order="name",
    )
    assert calls and calls[0][0] == "glossary"
    assert calls[0][1] == "2025"
    assert calls[0][2]["q"] == "lymph"
    assert calls[0][2]["category"] == "GENERAL,STAGING"

def test_glossary_changelog(monkeypatch):
    calls = _install_spy(monkeypatch, seer_glossary)
    seer_glossary.list_glossary_changelog(DummyClient(), "2025", from_date="2025-01-01", count=99)
    assert calls[0][1] == "2025/changelog"
    # count capped at 10
    assert calls[0][2]["count"] == 10

def test_glossary_by_id(monkeypatch):
    calls = _install_spy(monkeypatch, seer_glossary)
    seer_glossary.get_glossary_by_id(DummyClient(), "2025", "ABC123", glossary=True)
    assert calls[0][1] == "2025/id/ABC123"
    assert calls[0][2]["glossary"] == "true"

def test_glossary_keywords(monkeypatch):
    calls = _install_spy(monkeypatch, seer_glossary)
    seer_glossary.list_glossary_keywords(DummyClient(), "2025", q="node", count=20)
    assert calls[0][1] == "2025/keywords"
    assert calls[0][2]["q"] == "node"

def test_glossary_status_summary(monkeypatch):
    calls = _install_spy(monkeypatch, seer_glossary)
    seer_glossary.list_glossary_status_summary(DummyClient(), "2025")
    assert calls[0][1] == "2025/status_summary"

def test_glossary_versions(monkeypatch):
    calls = _install_spy(monkeypatch, seer_glossary)
    seer_glossary.list_glossary_versions(DummyClient())
    assert calls[0][1] == "versions"

# -------------------- DISEASE --------------------
from ind.seer import disease as seer_disease

def test_disease_list(monkeypatch):
    calls = _install_spy(monkeypatch, seer_disease)
    seer_disease.list_diseases(DummyClient(), "2025", type="HEMATO", count=10)
    assert calls[0][0] == "disease"
    assert calls[0][1] == "2025"
    assert calls[0][2]["type"] == "HEMATO"

def test_disease_changelog(monkeypatch):
    calls = _install_spy(monkeypatch, seer_disease)
    seer_disease.list_disease_changelog(DummyClient(), "2025", from_date="2025-01-01", order="ASC")
    assert calls[0][1] == "2025/changelog"
    assert calls[0][2]["order"] == "ASC"

def test_disease_by_id(monkeypatch):
    calls = _install_spy(monkeypatch, seer_disease)
    seer_disease.get_disease_by_id(DummyClient(), "2025", "D123")
    assert calls[0][1] == "2025/id/D123"

def test_disease_by_id_year(monkeypatch):
    calls = _install_spy(monkeypatch, seer_disease)
    seer_disease.get_disease_by_id_year(DummyClient(), "2025", "D123", "2020")
    assert calls[0][1] == "2025/id/D123/2020"

def test_disease_keywords(monkeypatch):
    calls = _install_spy(monkeypatch, seer_disease)
    seer_disease.list_disease_keywords(DummyClient(), "2025", q="lymph")
    assert calls[0][1] == "2025/keywords"

def test_disease_compare(monkeypatch):
    calls = _install_spy(monkeypatch, seer_disease)
    seer_disease.is_same_disease(DummyClient(), "1.0", d1="8000/3", year1="2001", d2="8140/3", year2="2015")
    assert calls[0][1] == "1.0/same"
    assert calls[0][2]["d1"] == "8000/3"

def test_disease_status_summary(monkeypatch):
    calls = _install_spy(monkeypatch, seer_disease)
    seer_disease.list_disease_status_summary(DummyClient(), "2025")
    assert calls[0][1] == "2025/status_summary"

def test_disease_primary_site(monkeypatch):
    calls = _install_spy(monkeypatch, seer_disease)
    seer_disease.list_disease_primary_sites(DummyClient())
    assert calls[0][1] == "primary_site"
    seer_disease.get_disease_primary_site_by_code(DummyClient(), "C50")
    assert calls[1][1] == "primary_site/C50"

def test_disease_site_categories_and_versions(monkeypatch):
    calls = _install_spy(monkeypatch, seer_disease)
    seer_disease.list_disease_site_categories(DummyClient())
    seer_disease.list_disease_versions(DummyClient())
    assert calls[0][1] == "site_categories"
    assert calls[1][1] == "versions"

# -------------------- HCPCS --------------------
from ind.seer import hcpcs as seer_hcpcs

def test_hcpcs_list_and_code(monkeypatch):
    calls = _install_spy(monkeypatch, seer_hcpcs)
    seer_hcpcs.list_hcpcs(DummyClient(), q="bevacizumab", order="-date_modified")
    seer_hcpcs.get_hcpcs_by_code(DummyClient(), "J9035")
    assert calls[0][1] == ""
    assert calls[1][1] == "code/J9035"

# -------------------- MPH --------------------
from ind.seer import mph as seer_mph

def test_mph_group_and_groups(monkeypatch):
    calls = _install_spy(monkeypatch, seer_mph)
    seer_mph.get_mph_group_by_id(DummyClient(), "BREAST_2018")
    seer_mph.list_mph_groups(DummyClient())
    assert calls[0][1] == "group/BREAST_2018"
    assert calls[1][1] == "groups"

# -------------------- NAACCR (SEER) --------------------
from ind.seer import naaccr as seer_naaccr

def test_naaccr_items_and_by_id_and_versions(monkeypatch):
    calls = _install_spy(monkeypatch, seer_naaccr)
    seer_naaccr.list_naaccr_items(DummyClient(), "22", q="primary site", count=50)
    seer_naaccr.get_naaccr_item_by_id(DummyClient(), "22", "primarySite")
    seer_naaccr.list_naaccr_versions(DummyClient())
    assert calls[0][1] == "22"
    assert calls[1][1] == "22/primarySite"
    assert calls[2][1] == "versions"

# -------------------- NDC --------------------
from ind.seer import ndc as seer_ndc

def test_ndc_list_and_code(monkeypatch):
    calls = _install_spy(monkeypatch, seer_ndc)
    seer_ndc.list_ndc(DummyClient(), q="bevacizumab", category=["CHEMOTHERAPY"], has_seer_info=True)
    seer_ndc.get_ndc_by_code(DummyClient(), "50242-060-01")
    assert calls[0][1] == ""
    assert calls[0][2]["category"] == "CHEMOTHERAPY"
    assert calls[0][2]["has_seer_info"] == "true"
    assert calls[1][1] == "code/50242-060-01"

# -------------------- RECODE --------------------
from ind.seer import recode as seer_recode

def test_recode_sitegroup_and_algorithms(monkeypatch):
    calls = _install_spy(monkeypatch, seer_recode)
    seer_recode.get_site_group(DummyClient(), "seer", site="C34.9", hist="8140/3", behavior="3")
    seer_recode.list_sitegroup_algorithms(DummyClient())
    assert calls[0][1] == "sitegroup/seer"
    assert calls[0][2]["site"] == "C34.9"
    assert calls[1][1] == "sitegroup/algorithms"

# -------------------- RX --------------------
from ind.seer import rx as seer_rx

def test_rx_list_and_helpers(monkeypatch):
    calls = _install_spy(monkeypatch, seer_rx)
    seer_rx.list_rx(DummyClient(), "2025", q="bevacizumab", type="DRUG", category=["CHEMOTHERAPY"], do_not_code="NO")
    seer_rx.list_rx_changelog(DummyClient(), "2025", count=99)
    seer_rx.get_rx_by_id(DummyClient(), "2025", "RX123", glossary=True)
    seer_rx.list_rx_regimens_for_drug(DummyClient(), "2025", "RX123")
    seer_rx.list_rx_keywords(DummyClient(), "2025", q="bev", count=10)
    seer_rx.list_rx_status_summary(DummyClient(), "2025")
    seer_rx.list_rx_versions(DummyClient())
    assert calls[0][1] == "2025"
    assert calls[0][2]["category"] == "CHEMOTHERAPY"
    assert calls[1][2]["count"] == 10  # capped
    assert calls[2][1] == "2025/id/RX123"
    assert calls[3][1] == "2025/id/RX123/regimens"
    assert calls[4][1] == "2025/keywords"
    assert calls[6][1] == "versions"

# -------------------- STAGING --------------------
from ind.seer import staging as seer_staging

def test_staging_all_endpoints(monkeypatch):
    calls = _install_spy(monkeypatch, seer_staging)
    seer_staging.get_staging_algorithm(DummyClient(), "ajcc8")
    seer_staging.get_staging_algorithm_version(DummyClient(), "ajcc8", "1.1")
    seer_staging.get_staging_schema_by_id(DummyClient(), "ajcc8", "1.1", "lung")
    seer_staging.get_staging_schema_glossary(DummyClient(), "ajcc8", "1.1", "lung", category=["GENERAL"]) 
    seer_staging.get_staging_schema_history(DummyClient(), "ajcc8", "1.1", "lung", order="DESC")
    seer_staging.list_staging_schema_tables(DummyClient(), "ajcc8", "1.1", "lung")
    seer_staging.list_staging_schemas(DummyClient(), "ajcc8", "1.1", q="lung")
    seer_staging.list_staging_schemas_history(DummyClient(), "ajcc8", "1.1", order="ASC")
    seer_staging.get_staging_table_by_id(DummyClient(), "ajcc8", "1.1", "t-category")
    seer_staging.get_staging_table_glossary(DummyClient(), "ajcc8", "1.1", "t-category", whole_words_only=False)
    seer_staging.get_staging_table_history(DummyClient(), "ajcc8", "1.1", "t-category")
    seer_staging.list_staging_table_schemas(DummyClient(), "ajcc8", "1.1", "t-category")
    seer_staging.list_staging_tables(DummyClient(), "ajcc8", "1.1", q="category", unused=True)
    seer_staging.list_staging_tables_history(DummyClient(), "ajcc8", "1.1", order="DESC")
    seer_staging.list_staging_algorithm_versions(DummyClient(), "ajcc8")
    seer_staging.list_staging_algorithms(DummyClient())

    # spot-check a few
    assert calls[0][1] == "ajcc8"
    assert calls[2][1] == "ajcc8/1.1/schema/lung"
    assert calls[3][2]["category"] == "GENERAL"
    assert calls[9][2]["wholeWordsOnly"] == "false"
    assert calls[14][1] == "ajcc8/versions"
    assert calls[15][1] == "algorithms"

# -------------------- SURGERY --------------------
from ind.seer import surgery as seer_surgery

def test_surgery_table_and_tables(monkeypatch):
    calls = _install_spy(monkeypatch, seer_surgery)
    seer_surgery.get_surgery_table(DummyClient(), "latest", site="C50.9", hist="8500/3")
    seer_surgery.list_surgery_tables(DummyClient(), "latest")
    assert calls[0][1] == "latest/table"
    assert calls[0][2]["site"] == "C50.9"
    assert calls[1][1] == "latest/tables"