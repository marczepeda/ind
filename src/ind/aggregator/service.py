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

# Retrieve NDC directory records for a company
def _search_ndc_directory(company: str, limit: int = 1000) -> List[Dict[str, Any]]:
    client = OpenFDAClient()
    q_company = company.upper()
    # NDC records commonly include labeler_name; also try openfda.manufacturer_name for broader matches
    query = f'labeler_name:"{q_company}" OR openfda.manufacturer_name:"{q_company}"'
    params = {"search": query, "limit": 100, "skip": 0}
    try:
        return _openfda_paged(client, "/drug/ndc.json", params, limit=limit)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return []
        raise

# Retrieve drug adverse event reports for a company
def _search_drug_adverse_events(company: str, limit: int = 1000) -> List[Dict[str, Any]]:
    client = OpenFDAClient()
    q_company = company.upper()

    # FAERS fields are nested under patient.drug.openfda.*
    # Manufacturer can appear as manufacturer_name; brand/generic are also in openfda.
    # We bias toward manufacturer_name because it most directly matches company.
    query = (
        f'patient.drug.openfda.manufacturer_name:"{q_company}" '
        f'OR patient.drug.openfda.sponsor_name:"{q_company}" '
        f'OR patient.drug.openfda.application_number:"{q_company}"'
    )

    params = {"search": query, "limit": 100, "skip": 0}
    try:
        return _openfda_paged(client, "/drug/event.json", params, limit=limit)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return []
        raise

# Retrieve drug enforcement (recall) reports for a company
def _search_drug_enforcements(company: str, limit: int = 1000) -> List[Dict[str, Any]]:
    client = OpenFDAClient()
    q_company = company.upper()

    # Enforcement records commonly use recalling_firm; also sometimes manufacturer_name.
    query = f'recalling_firm:"{q_company}" OR manufacturer_name:"{q_company}"'
    params = {"search": query, "limit": 100, "skip": 0}
    try:
        return _openfda_paged(client, "/drug/enforcement.json", params, limit=limit)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return []
        raise

# Retrieve drug shortages records for a company
def _search_drug_shortages(company: str, limit: int = 1000) -> List[Dict[str, Any]]:
    client = OpenFDAClient()
    q_company = company.upper()

    # Drug shortages exposes `company_name` as a searchable field.
    # We also include openfda.manufacturer_name as a fallback when present.
    query = f'company_name:"{q_company}" OR openfda.manufacturer_name:"{q_company}"'
    params = {"search": query, "limit": 100, "skip": 0}
    try:
        return _openfda_paged(client, "/drug/shortages.json", params, limit=limit)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return []
        raise


# Flatten drug shortages records for CSV/table
def _flatten_drug_shortages(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    def join_list(x) -> str:
        if isinstance(x, list):
            return "; ".join([str(v) for v in x if v is not None and str(v) != ""])
        return "" if x is None else str(x)

    for r in records:
        openfda = r.get("openfda") or {}
        rows.append({
            "package_ndc": r.get("package_ndc") or "",
            "generic_name": r.get("generic_name") or "",
            "proprietary_name": r.get("proprietary_name") or "",
            "company_name": r.get("company_name") or "",
            "status": r.get("status") or "",
            "availability": r.get("availability") or "",
            "shortage_reason": r.get("shortage_reason") or "",
            "dosage_form": r.get("dosage_form") or "",
            "therapeutic_category": join_list(r.get("therapeutic_category")),
            "strength": join_list(r.get("strength")),
            "presentation": r.get("presentation") or "",
            "update_type": r.get("update_type") or "",
            "update_date": r.get("update_date") or "",
            "change_date": r.get("change_date") or "",
            "initial_posting_date": r.get("initial_posting_date") or "",
            "discontinued_date": r.get("discontinued_date") or "",
            "resolved_note": r.get("resolved_note") or "",
            "related_info": r.get("related_info") or "",
            "related_info_link": r.get("related_info_link") or "",
            "manufacturer_name": join_list(openfda.get("manufacturer_name")),
        })

    for row in rows:
        for k, v in list(row.items()):
            if v is None:
                row[k] = ""

    return rows

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

# Flatten NDC directory records for CSV/table
def _flatten_ndc_directory(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for r in records:
        openfda = r.get("openfda") or {}
        # openfda fields are often arrays
        def first(x):
            return x[0] if isinstance(x, list) and x else (x or "")

        rows.append({
            "product_ndc": r.get("product_ndc") or "",
            "generic_name": r.get("generic_name") or "",
            "brand_name": r.get("brand_name") or "",
            "labeler_name": r.get("labeler_name") or "",
            "dosage_form": r.get("dosage_form") or "",
            "route": "; ".join(r.get("route") or []) if isinstance(r.get("route"), list) else (r.get("route") or ""),
            "marketing_category": r.get("marketing_category") or "",
            "product_type": r.get("product_type") or "",
            "finished": r.get("finished") if r.get("finished") is not None else "",
            "listing_expiration_date": r.get("listing_expiration_date") or "",
            "manufacturer_name": "; ".join(openfda.get("manufacturer_name") or []) if isinstance(openfda.get("manufacturer_name"), list) else first(openfda.get("manufacturer_name")),
        })

    # Normalize None to empty strings
    for row in rows:
        for k, v in list(row.items()):
            if v is None:
                row[k] = ""

    return rows

# Flatten FAERS (drug adverse event) records for CSV/table
def _flatten_drug_adverse_events(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    def first(x, default: str = ""):
        if isinstance(x, list):
            return x[0] if x else default
        return x if x is not None else default

    for r in records:
        safetyreportid = r.get("safetyreportid") or ""
        receivedate = r.get("receivedate") or ""
        receiptdate = r.get("receiptdate") or ""
        serious = r.get("serious") if r.get("serious") is not None else ""

        patient = r.get("patient") or {}
        patientsex = patient.get("patientsex") if patient.get("patientsex") is not None else ""
        patientagegroup = patient.get("patientagegroup") if patient.get("patientagegroup") is not None else ""

        # Reactions: collect preferred terms
        reactions = []
        for rxn in (patient.get("reaction") or []):
            if isinstance(rxn, dict):
                pt = rxn.get("reactionmeddrapt") or rxn.get("reactionmeddra")
                if pt:
                    reactions.append(str(pt))
            elif isinstance(rxn, str):
                reactions.append(rxn)
        reaction_pt = "; ".join(dict.fromkeys(reactions))  # de-dupe, keep order

        # Drugs: collect medicinal product names and manufacturers if present
        meds = []
        mfgs = []
        for d in (patient.get("drug") or []):
            if not isinstance(d, dict):
                continue
            mp = d.get("medicinalproduct")
            if mp:
                meds.append(str(mp))
            of = d.get("openfda") or {}
            m = of.get("manufacturer_name")
            if isinstance(m, list):
                mfgs.extend([str(x) for x in m if x])
            elif m:
                mfgs.append(str(m))

        medicinalproduct = "; ".join(dict.fromkeys(meds))
        manufacturer_name = "; ".join(dict.fromkeys(mfgs))

        rows.append({
            "safetyreportid": safetyreportid,
            "receivedate": receivedate,
            "receiptdate": receiptdate,
            "serious": serious,
            "patientsex": patientsex,
            "patientagegroup": patientagegroup,
            "medicinalproduct": medicinalproduct,
            "manufacturer_name": manufacturer_name,
            "reaction_pt": reaction_pt,
        })

    for row in rows:
        for k, v in list(row.items()):
            if v is None:
                row[k] = ""

    return rows

# Flatten drug enforcement (recall) records for CSV/table
def _flatten_drug_enforcements(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    keep = [
        "recall_number",
        "recalling_firm",
        "product_description",
        "reason_for_recall",
        "classification",
        "status",
        "report_date",
        "recall_initiation_date",
        "termination_date",
        "city",
        "state",
        "country",
        "distribution_pattern",
        "code_info",
    ]

    for r in records:
        row: Dict[str, Any] = {}
        for k in keep:
            v = r.get(k)
            row[k] = "" if v is None else v
        rows.append(row)

    return rows

def _search_drug_labels(company: str, limit: int = 1000) -> List[Dict[str, Any]]:
    client = OpenFDAClient()
    q_company = company.upper()
    query = f'openfda.manufacturer_name:"{q_company}"'
    params = {"search": query, "limit": 100, "skip": 0}
    try:
        return _openfda_paged(client, "/drug/label.json", params, limit=limit)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return []
        raise


def _flatten_drug_labels(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    def join_list(x) -> str:
        if isinstance(x, list):
            return "; ".join([str(v) for v in x if v is not None and str(v) != ""])
        return "" if x is None else str(x)

    for r in records:
        of = r.get("openfda") or {}
        rows.append({
            "id": r.get("id") or "",
            "set_id": r.get("set_id") or "",
            "effective_time": r.get("effective_time") or "",
            "version": r.get("version") or "",
            "brand_name": join_list(of.get("brand_name")),
            "generic_name": join_list(of.get("generic_name")),
            "manufacturer_name": join_list(of.get("manufacturer_name")),
            "product_ndc": join_list(of.get("product_ndc")),
            "package_ndc": join_list(of.get("package_ndc")),
            "route": join_list(of.get("route")),
            "dosage_form": join_list(of.get("dosage_form")),
            "application_number": join_list(of.get("application_number")),
            "spl_id": join_list(of.get("spl_id")),
            "spl_set_id": join_list(of.get("spl_set_id")),
        })

    return rows

@dataclass
class CompanyOpenFDAIntel:
    company: str
    drugs_approved: List[Dict[str, Any]]
    devices_510k: List[Dict[str, Any]]
    devices_pma: List[Dict[str, Any]]
    ndc_directory: List[Dict[str, Any]]
    drug_adverse_events: List[Dict[str, Any]]
    drug_enforcements: List[Dict[str, Any]]
    drug_labels: List[Dict[str, Any]]
    drug_shortages: List[Dict[str, Any]]

    def dict(self) -> Dict[str, Any]:
        return asdict(self)

def build_company_intel(company: str, *, max_records: int = 1000) -> CompanyOpenFDAIntel:
    """
    OpenFDA-only aggregator:
      - Looks up drugs approved for a given sponsor/company via /drug/drugsfda
      - Looks up devices (510k and PMA) for a company via /device/510k and /device/pma
      - Looks up NDC directory for a company via /drug/ndc
      - Looks up Drug Adverse Events (FAERS) for a company via /drug/event
      - Looks up Drug Enforcement Reports (Recalls) for a company via /drug/enforcement
    """
    records = _search_sponsor(company, limit=max_records)
    drugs = _flatten_approved_drugs(records)

    ndc_records = _search_ndc_directory(company, limit=max_records)
    ndc_directory = _flatten_ndc_directory(ndc_records)

    ae_records = _search_drug_adverse_events(company, limit=max_records)
    drug_adverse_events = _flatten_drug_adverse_events(ae_records)

    enf_records = _search_drug_enforcements(company, limit=max_records)
    drug_enforcements = _flatten_drug_enforcements(enf_records)

    label_records = _search_drug_labels(company, limit=max_records)
    drug_labels = _flatten_drug_labels(label_records)

    shortage_records = _search_drug_shortages(company, limit=max_records)
    drug_shortages = _flatten_drug_shortages(shortage_records)

    dev_510k_records = _search_device_510k(company, limit=max_records)
    dev_pma_records = _search_device_pma(company, limit=max_records)
    dev_510k = _flatten_510k(dev_510k_records)
    dev_pma = _flatten_pma(dev_pma_records)

    return CompanyOpenFDAIntel(
        company=company,
        drugs_approved=drugs,
        devices_510k=dev_510k,
        devices_pma=dev_pma,
        ndc_directory=ndc_directory,
        drug_adverse_events=drug_adverse_events,
        drug_enforcements=drug_enforcements,
        drug_labels=drug_labels,
        drug_shortages=drug_shortages,
    )