from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
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
    print(set(none_ls))
            
    return rows

'''def _flatten_approved_drugs(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Compact entries with: brand_name, active_ingredient, application, approval_date
    """
    rows: List[Dict[str, Any]] = []
    for r in records:
        appl_no = r.get("application_number") or r.get("appl_no") or ""
        # approval date from first approved/Original submission if present
        approval_date = ""
        for sub in r.get("submissions", []) or []:
            status = (sub.get("submission_status") or "").lower()
            if "approved" in status:
                approval_date = sub.get("submission_status_date") or sub.get("submission_public_date") or ""
                break
        for p in r.get("products", []) or []:
            brand = _coerce_first(p.get("brand_name"))
            # active_ingredients may be a list of dicts with {name}
            ai = ""
            if isinstance(p.get("active_ingredients"), list) and p["active_ingredients"]:
                names = []
                for ai_item in p["active_ingredients"]:
                    name = ai_item.get("name") if isinstance(ai_item, dict) else ai_item
                    if name:
                        names.append(str(name))
                ai = "; ".join(names)
            else:
                ai = _coerce_first(p.get("active_ingredients"), "")
            rows.append({
                "brand_name": brand,
                "active_ingredient": ai,
                "application": appl_no,
                "approval_date": approval_date,
            })
    # de-duplicate identical rows
    seen = set()
    deduped = []
    for row in rows:
        key = (row["brand_name"], row["active_ingredient"], row["application"], row["approval_date"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped'''

@dataclass
class CompanyOpenFDAIntel:
    company: str
    drugs_approved: List[Dict[str, Any]]

    def dict(self) -> Dict[str, Any]:
        return asdict(self)

def build_company_intel(company: str, *, max_records: int = 1000) -> CompanyOpenFDAIntel:
    """
    OpenFDA-only aggregator:
      - Looks up drugs approved for a given sponsor/company via /drug/drugsfda
    """
    records = _search_sponsor(company, limit=max_records)
    drugs = _flatten_approved_drugs(records)
    return CompanyOpenFDAIntel(company=company, drugs_approved=drugs)