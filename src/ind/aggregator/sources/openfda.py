from typing import Any, Dict, List
import requests
from ...openfda.client import OpenFDAClient
from ..utils import _coerce_first

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

# Retrieve device adverse event (MDR) reports for a company
def _search_device_adverse_events(company: str, limit: int = 1000) -> List[Dict[str, Any]]:
    client = OpenFDAClient()
    q_company = company.upper()

    # Device event records commonly use top-level manufacturer_name; openfda.manufacturer_name can also exist.
    query = f'manufacturer_name:"{q_company}" OR openfda.manufacturer_name:"{q_company}"'
    params = {"search": query, "limit": 100, "skip": 0}
    try:
        return _openfda_paged(client, "/device/event.json", params, limit=limit)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return []
        raise

# Flatten device adverse event (MDR) records for CSV/table
def _flatten_device_adverse_events(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    def join_list(x) -> str:
        if isinstance(x, list):
            return "; ".join([str(v) for v in x if v is not None and str(v) != ""])
        return "" if x is None else str(x)

    # de-dupe while preserving order
    def dedupe(xs: List[str]) -> str:
        out: List[str] = []
        seen = set()
        for x in xs:
            if not x or x in seen:
                continue
            seen.add(x)
            out.append(x)
        return "; ".join(out)

    for r in records:
        devs = r.get("device") or []
        if not isinstance(devs, list):
            devs = []

        brand_names: List[str] = []
        generic_names: List[str] = []
        product_codes: List[str] = []
        for d in devs:
            if not isinstance(d, dict):
                continue
            bn = d.get("brand_name")
            if bn:
                brand_names.append(str(bn))
            gn = d.get("generic_name")
            if gn:
                generic_names.append(str(gn))
            pc = d.get("device_report_product_code") or d.get("product_code")
            if pc:
                product_codes.append(str(pc))

        rows.append({
            "mdr_report_key": r.get("mdr_report_key") or "",
            "report_number": r.get("report_number") or "",
            "date_received": r.get("date_received") or "",
            "date_of_event": r.get("date_of_event") or "",
            "report_date": r.get("report_date") or "",
            "event_type": r.get("event_type") or "",
            "manufacturer_name": r.get("manufacturer_name") or "",
            "brand_name": dedupe(brand_names),
            "generic_name": dedupe(generic_names),
            "product_code": dedupe(product_codes),
            "product_problem_flag": r.get("product_problem_flag") or "",
            "adverse_event_flag": r.get("adverse_event_flag") or "",
            "product_problem_text": join_list(r.get("product_problem_text")),
            "patient_problem_text": join_list(r.get("patient_problem_text")),
        })

    for row in rows:
        for k, v in list(row.items()):
            if v is None:
                row[k] = ""

    return rows

# Retrieve device enforcement (recall) reports for a company
def _search_device_enforcements(company: str, limit: int = 1000) -> List[Dict[str, Any]]:
    client = OpenFDAClient()
    q_company = company.upper()

    # Device enforcement records commonly use recalling_firm; also sometimes manufacturer_name.
    query = f'recalling_firm:"{q_company}" OR manufacturer_name:"{q_company}"'
    params = {"search": query, "limit": 100, "skip": 0}
    try:
        return _openfda_paged(client, "/device/enforcement.json", params, limit=limit)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return []
        raise

# Flatten device enforcement (recall) records for CSV/table
def _flatten_device_enforcements(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
        "center_classification_date",
        "termination_date",
        "event_id",
        "product_code",
        "product_type",
        "city",
        "state",
        "country",
        "distribution_pattern",
        "code_info",
        "voluntary_mandated",
    ]

    for r in records:
        row: Dict[str, Any] = {}
        for k in keep:
            v = r.get(k)
            row[k] = "" if v is None else v
        rows.append(row)

    return rows

# Retrieve device recall reports for a company
def _search_device_recalls(company: str, limit: int = 1000) -> List[Dict[str, Any]]:
    client = OpenFDAClient()
    q_company = company.upper()

    # Recall records commonly use recalling_firm; sometimes manufacturer_name too.
    query = f'recalling_firm:"{q_company}" OR manufacturer_name:"{q_company}"'
    params = {"search": query, "limit": 100, "skip": 0}
    try:
        return _openfda_paged(client, "/device/recall.json", params, limit=limit)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return []
        raise

# Flatten device recall records for CSV/table
def _flatten_device_recalls(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    keep = [
        "recall_number",
        "recalling_firm",
        "product_description",
        "reason_for_recall",
        "status",
        "report_date",
        "recall_initiation_date",
        "termination_date",
        "event_id",
        "product_code",
        "product_type",
        "city",
        "state",
        "country",
        "distribution_pattern",
        "code_info",
        "voluntary_mandated",
    ]

    for r in records:
        row: Dict[str, Any] = {}
        for k in keep:
            v = r.get(k)
            row[k] = "" if v is None else v
        rows.append(row)

    return rows

# Retrieve device registration & listing records for a company
def _search_device_registrationlisting(company: str, limit: int = 1000) -> List[Dict[str, Any]]:
    client = OpenFDAClient()
    q_company = company.upper()

    # Try multiple common match points for the company name
    query = (
        f'registration.owner_operator.firm_name:"{q_company}" '
        f'OR registration.name:"{q_company}" '
        f'OR registration.us_agent.business_name:"{q_company}" '
        f'OR registration.us_agent.name:"{q_company}"'
    )
    params = {"search": query, "limit": 100, "skip": 0}
    try:
        return _openfda_paged(client, "/device/registrationlisting.json", params, limit=limit)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return []
        raise


def _flatten_device_registrationlisting(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    def join_list(x) -> str:
        if isinstance(x, list):
            return "; ".join([str(v) for v in x if v is not None and str(v) != ""])
        return "" if x is None else str(x)

    def first(x, default: str = "") -> str:
        if isinstance(x, list):
            return str(x[0]) if x else default
        return default if x is None else str(x)

    def dedupe(xs: List[str]) -> str:
        out: List[str] = []
        seen = set()
        for x in xs:
            if not x or x in seen:
                continue
            seen.add(x)
            out.append(x)
        return "; ".join(out)

    for r in records:
        reg = r.get("registration") or {}
        owner = reg.get("owner_operator") or {}
        contact = owner.get("contact_address") or {}
        us_agent = reg.get("us_agent") or {}

        products = r.get("products") or []
        if not isinstance(products, list):
            products = []

        product_codes: List[str] = []
        k_numbers: List[str] = []
        pma_numbers: List[str] = []
        exempt_flags: List[str] = []

        for p in products:
            if not isinstance(p, dict):
                continue
            pc = p.get("product_code")
            if pc:
                product_codes.append(str(pc))
            kn = p.get("k_number")
            if kn:
                k_numbers.append(str(kn))
            pn = p.get("pma_number")
            if pn:
                pma_numbers.append(str(pn))
            ex = p.get("exempt")
            if ex is not None and str(ex) != "":
                exempt_flags.append(str(ex))

        rows.append({
            "registration_number": reg.get("registration_number") or "",
            "fei_number": reg.get("fei_number") or "",
            "registration_status_code": reg.get("status_code") or "",
            "initial_importer_flag": reg.get("initial_importer_flag") or "",
            "reg_expiry_date_year": reg.get("reg_expiry_date_year") or "",
            "facility_name": reg.get("name") or "",
            "facility_city": reg.get("city") or "",
            "facility_state_code": reg.get("state_code") or "",
            "facility_iso_country_code": reg.get("iso_country_code") or "",

            "owner_operator_number": owner.get("owner_operator_number") or "",
            "owner_operator_firm_name": owner.get("firm_name") or "",
            "owner_operator_city": contact.get("city") or "",
            "owner_operator_state_code": contact.get("state_code") or "",
            "owner_operator_iso_country_code": contact.get("iso_country_code") or "",

            "us_agent_name": us_agent.get("name") or "",
            "us_agent_business_name": us_agent.get("business_name") or "",
            "us_agent_city": us_agent.get("city") or "",
            "us_agent_state_code": us_agent.get("state_code") or "",
            "us_agent_iso_country_code": us_agent.get("iso_country_code") or "",

            "proprietary_name": join_list(r.get("proprietary_name")),
            "establishment_type": join_list(r.get("establishment_type")),

            "product_code": dedupe(product_codes),
            "k_number": dedupe(k_numbers),
            "pma_number": dedupe(pma_numbers),
            "exempt": dedupe(exempt_flags),

            # openfda fields sometimes present at top-level
            "device_class": first(r.get("device_class")),
            "medical_specialty_description": first(r.get("medical_specialty_description")),
            "regulation_number": join_list(r.get("regulation_number")),
        })

    for row in rows:
        for k, v in list(row.items()):
            if v is None:
                row[k] = ""

    return rows

def _search_transparency_crl(company: str, limit: int = 1000) -> List[Dict[str, Any]]:
    client = OpenFDAClient()
    q_company = (company or "").strip()
    if not q_company:
        return []

    q_upper = q_company.upper()

    # CRL fields: company_name/company_rep/company_address plus full-text `text`.
    # Use a broad OR query to increase match rate.
    query = (
        f'company_name:"{q_company}" OR company_name:"{q_upper}" '
        f'OR company_rep:"{q_company}" OR company_rep:"{q_upper}" '
        f'OR company_address:"{q_company}" OR company_address:"{q_upper}" '
        f'OR text:"{q_company}"'
    )

    params = {"search": query, "limit": 100, "skip": 0}
    try:
        return _openfda_paged(client, "/transparency/crl.json", params, limit=limit)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return []
        raise


def _flatten_transparency_crl(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    keep = [
        "file_name",
        "application_number",
        "letter_date",
        "letter_type",
        "approval_name",
        "approval_title",
        "approval_center",
        "company_name",
        "company_rep",
        "company_address",
    ]

    for r in records:
        row: Dict[str, Any] = {}
        for k in keep:
            v = r.get(k)
            row[k] = "" if v is None else v
        rows.append(row)

    return rows