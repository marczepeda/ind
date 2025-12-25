from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple
import requests
from ind.openfda.client import OpenFDAClient

def _coerce_first(xs, default: str = "") -> str:
    if isinstance(xs, list):
        return xs[0] if xs else default
    return xs or default

def _openfda_page(client: OpenFDAClient, params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return client.request_json("GET", "/drug/drugsfda.json", params=params)
    except requests.HTTPError as e:
        # OpenFDA returns 404 when the query has no matches. Treat as empty results.
        if e.response is not None and e.response.status_code == 404:
            return {"results": [], "meta": {"results": {"total": 0}}}
        raise


# Generic OpenFDA paging helper for any endpoint
def _openfda_paged(client: OpenFDAClient, path: str, params: Dict[str, Any], *, limit: int = 1000) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    page_size = int(params.get("limit") or 100)
    params = dict(params)
    params["limit"] = page_size
    params.setdefault("skip", 0)

    data = client.request_json("GET", path, params=params)
    results = data.get("results", []) or []
    out.extend(results)
    total = data.get("meta", {}).get("results", {}).get("total", len(results))
    total = min(int(total or 0), limit)

    fetched = len(results)
    while fetched < total:
        params["skip"] = fetched
        data = client.request_json("GET", path, params=params)
        results = data.get("results", []) or []
        if not results:
            break
        out.extend(results)
        fetched += len(results)

    return out[:total]

def _search_sponsor(company: str, limit: int = 1000) -> List[Dict[str, Any]]:
    """
    Query OpenFDA /drug/drugsfda for a sponsor/company with pagination.
    """
    client = OpenFDAClient()
    out: List[Dict[str, Any]] = []
    page_size = 100
    query = f'sponsor_name:"{company.upper()}"' # Make upper case
    params = {"search": query, "limit": page_size, "skip": 0}

    data = _openfda_page(client, params)
    results = data.get("results", []) or []
    out.extend(results)
    total = data.get("meta", {}).get("results", {}).get("total", len(results))
    total = min(int(total or 0), limit)

    fetched = len(results)
    while fetched < total:
        params["skip"] = fetched
        data = _openfda_page(client, params)
        results = data.get("results", []) or []
        if not results:
            break
        out.extend(results)
        fetched += len(results)

    return out[:total]


# Retrieve 510k devices for a company
def _search_device_510k(company: str, limit: int = 1000) -> List[Dict[str, Any]]:
    client = OpenFDAClient()
    q_company = company.upper()
    # Common fields for company name in 510k records
    query = f'applicant:"{q_company}" OR manufacturer_name:"{q_company}"'
    params = {"search": query, "limit": 100, "skip": 0}
    try:
        return _openfda_paged(client, "/device/510k.json", params, limit=limit)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return []
        raise


# Retrieve PMA devices for a company
def _search_device_pma(company: str, limit: int = 1000) -> List[Dict[str, Any]]:
    client = OpenFDAClient()
    q_company = company.upper()
    query = f'applicant:"{q_company}" OR manufacturer_name:"{q_company}"'
    params = {"search": query, "limit": 100, "skip": 0}
    try:
        return _openfda_paged(client, "/device/pma.json", params, limit=limit)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return []
        raise

def _flatten_approved_drugs(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract extended info for each drug approval record.
    """
    rows: List[Dict[str, Any]] = []
    for r in records:
        appl_no = r.get("application_number")
        sponsor = r.get("sponsor_name")
        appl_type = r.get("application_type")
        for p in r.get("products", []) or []:
            brand = _coerce_first(p.get("brand_name"))
            dosage = p.get("dosage_form")
            route = p.get("route")
            marketing_status = p.get("marketing_status")
            product_no = p.get("product_number")

            active_ingredients = []
            for ai_item in p.get("active_ingredients", []):
                if isinstance(ai_item, dict) and ai_item.get("name"):
                    active_ingredients.append(ai_item["name"])
                elif isinstance(ai_item, str):
                    active_ingredients.append(ai_item)
            ai = "; ".join(active_ingredients)

            # Get first submission info
            sub = (r.get("submissions") or [{}])[0]
            submission_type = sub.get("submission_type")
            submission_status = sub.get("submission_status")
            submission_date = sub.get("submission_status_date")

            rows.append({
                "application": appl_no,
                #"application_type": appl_type,
                "sponsor": sponsor,
                "product_no": product_no,
                "brand_name": brand,
                "active_ingredient": ai,
                "dosage_form": dosage,
                "route": route,
                "marketing_status": marketing_status,
                #"submission_type": submission_type,
                #"submission_status": submission_status,
                #"submission_status_date": submission_date,
            })
    
    none_ls = []
    for row in rows:
        for k, v in row.items():
            if v is None:
                row[k] = ""
                none_ls.append(k)
    #print(set(none_ls))
            
    return rows


# Flatten 510k records for CSV/table
def _flatten_510k(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for r in records:
        rows.append({
            "k_number": r.get("k_number") or "",
            "device_name": r.get("device_name") or "",
            "applicant": r.get("applicant") or "",
            "manufacturer_name": r.get("manufacturer_name") or "",
            "product_code": r.get("product_code") or "",
            "advisory_committee": r.get("advisory_committee") or "",
            "clearance_type": r.get("clearance_type") or "",
            "decision_code": r.get("decision_code") or "",
            "decision_date": r.get("decision_date") or "",
        })
    return rows


# Flatten PMA records for CSV/table
def _flatten_pma(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for r in records:
        rows.append({
            "pma_number": r.get("pma_number") or "",
            "trade_name": r.get("trade_name") or "",
            "generic_name": r.get("generic_name") or "",
            "applicant": r.get("applicant") or "",
            "manufacturer_name": r.get("manufacturer_name") or "",
            "product_code": r.get("product_code") or "",
            "advisory_committee": r.get("advisory_committee") or "",
            "decision_code": r.get("decision_code") or "",
            "decision_date": r.get("decision_date") or "",
        })
    return rows

@dataclass
class CompanyOpenFDAIntel:
    company: str
    drugs_approved: List[Dict[str, Any]]
    devices_510k: List[Dict[str, Any]]
    devices_pma: List[Dict[str, Any]]

    def dict(self) -> Dict[str, Any]:
        return asdict(self)

def build_company_intel(company: str, *, max_records: int = 1000) -> CompanyOpenFDAIntel:
    """
    OpenFDA-only aggregator:
      - Looks up drugs approved for a given sponsor/company via /drug/drugsfda
      - Looks up devices (510k and PMA) for a company via /device/510k and /device/pma
    """
    records = _search_sponsor(company, limit=max_records)
    drugs = _flatten_approved_drugs(records)

    dev_510k_records = _search_device_510k(company, limit=max_records)
    dev_pma_records = _search_device_pma(company, limit=max_records)
    dev_510k = _flatten_510k(dev_510k_records)
    dev_pma = _flatten_pma(dev_pma_records)

    return CompanyOpenFDAIntel(
        company=company,
        drugs_approved=drugs,
        devices_510k=dev_510k,
        devices_pma=dev_pma,
    )