"""
High-level orchestration for company intelligence.

Assumptions: you already have modules like
 - ind.openfda.endpoints (drug approvals, applications)
 - ind.clinical_trials.endpoints (trial search/stats)
 - ind.naaccr.endpoints (population / incidence)
 - ind.uspto_odp.endpoints (patents, assignees)
 - ind.pubchem.endpoints (substance lookup)

You can swap imports to match your actual module paths.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from ind.openfda.client import OpenFDAClient
from ind.openfda.drug import search_drugsfda_by_sponsor_name, search_labels_by_application_number
from ind.naaccr.client import NAACCRClient
from ind.naaccr.endpoints import search_data_items

from ind.clinical_trials.client import ClinicalTrialsClient
from ind.clinical_trials.studies import list_studies, iterate_studies
from ind.uspto_odp import client as uspto_odp_client
from ind.pubchem import client as pubche_client

# OpenFDA
def get_drug_approvals_for_sponsor(sponsor: str) -> List[Dict[str, Any]]:
    """
    Use OpenFDA Drugs@FDA dataset to fetch applications by sponsor, and enrich with a short indication from labels.
    Returns a list of simplified dictionaries consumed by DrugRecord.
    """
    client = OpenFDAClient()

    def _normalize_date(d: Optional[str]) -> Optional[str]:
        if not d:
            return None
        s = str(d).strip()
        # Handle YYYY-MM-DD or YYYYMMDD
        if len(s) == 8 and s.isdigit():
            return f"{s[0:4]}-{s[4:6]}-{s[6:8]}"
        # crude validation for YYYY-MM-DD
        if len(s) == 10 and s[4] == "-" and s[7] == "-":
            return s
        return None

    # Pull applications/products for this sponsor
    resp = search_drugsfda_by_sponsor_name(client, sponsor)
    results = resp.results or []
    out: List[Dict[str, Any]] = []

    for r in results:
        app_no = r.get("application_number")
        products = r.get("products") or []
        brand = None
        active = None
        approval_date = None
        subs = r.get("submissions") or []
        orig_dates: List[str] = []
        all_dates: List[str] = []
        for sub in subs:
            ad = sub.get("action_date")
            nd = _normalize_date(ad)
            if not nd:
                continue
            all_dates.append(nd)
            st = (sub.get("submission_type") or "") or (sub.get("submissionclass") or "")
            st = str(st).upper()
            # Heuristic: prefer ORIGINAL approvals where possible
            if "ORIG" in st or "ORIGINAL" in st:
                orig_dates.append(nd)
        if orig_dates:
            approval_date = sorted(orig_dates)[0]   # earliest ORIGINAL submission
        elif all_dates:
            approval_date = sorted(all_dates)[0]    # fallback: earliest action date

        if products:
            first = products[0] or {}
            brand = first.get("brand_name")
            # active_ingredients is a list of dicts with "name"
            actives = first.get("active_ingredients") or []
            names = [a.get("name") for a in actives if isinstance(a, dict) and a.get("name")]
            active = ", ".join(names) if names else None
        else:
            # fallback to openfda block if present
            ofda = r.get("openfda") or {}
            brand_list = ofda.get("brand_name") or []
            brand = brand_list[0] if brand_list else None
            gen_list = ofda.get("generic_name") or []
            active = gen_list[0] if gen_list else None

        # Try to fetch a concise indication via label by application number
        indications: List[str] = []
        if app_no:
            try:
                lab = search_labels_by_application_number(client, app_no, limit=1)
                lab_res = (lab.results or [])
                if lab_res:
                    # labels typically have 'indications_and_usage' as a list of long strings
                    text_list = lab_res[0].get("indications_and_usage") or []
                    if text_list and isinstance(text_list, list):
                        first_text = text_list[0]
                        if isinstance(first_text, str):
                            # take the first sentence-ish as a short indication
                            short = first_text.split(".")[0].strip()
                            if short:
                                indications = [short]
            except Exception:
                # Be resilient to missing labels/fields
                pass

        out.append({
            "brand_name": brand,
            "application": app_no,
            "active_ingredient": active,
            "approval_date": approval_date,
            "indications": indications,
        })

    return out

def search_studies(company: str, drugs: List[DrugRecord], limit: int = 25) -> List[Dict[str, Any]]:
    """
    Query ClinicalTrials.gov v2 for studies related to the company and its drugs.
    Strategy:
    - Use query.spons with the company name (matches lead/sponsor/collaborators in Essie).
    - Use query.intr with a joined string of intervention names derived from brand/generic actives.
    - Request only the fields we need for TrialRecord.
    - Return a simplified list of dicts consumable by TrialRecord.
    """
    ct = ClinicalTrialsClient(rate_limit_per_sec=5.0)

    # Build intervention terms from drugs list (brand + active_ingredient tokens)
    intr_terms: List[str] = []
    for d in drugs:
        if d.brand_name:
            intr_terms.append(d.brand_name)
        if d.active_ingredient:
            # split on commas to capture multiple actives
            intr_terms.extend([p.strip() for p in d.active_ingredient.split(",") if p.strip()])
    # Deduplicate while preserving order
    seen = set()
    intr_terms = [t for t in intr_terms if not (t.lower() in seen or seen.add(t.lower()))]
    intr_query = " OR ".join(intr_terms) if intr_terms else None

    # Choose fields consistent with v2 /studies 'fields' projection
    fields = [
        "NCTId",
        "BriefTitle",
        "Phase",
        "OverallStatus",
        "Condition",
        "InterventionName",
        "LeadSponsorName",
    ]

    first_page_size = min(max(limit, 1), 100)
    page = list_studies(
        ct,
        query_spons=company,
        query_intr=intr_query,
        fields=fields,
        page_size=first_page_size,
        count_total=True,
        sort=["@relevance", "LastUpdatePostDate:desc"],
    )
    total = page.get("totalCount")
    studies_pages = [page]

    next_token = page.get("nextPageToken")
    if next_token and ( (isinstance(total, int) and total > 100) or (limit > first_page_size) ):
        # Use iterate_studies to fetch additional pages
        remaining = max(0, (min(total, limit) if isinstance(total, int) else limit) - first_page_size)
        if remaining > 0:
            # compute how many extra pages we need at page size 100
            extra_pages_needed = (remaining + 99) // 100
            pages = iterate_studies(
                ct,
                query_spons=company,
                query_intr=intr_query,
                fields=fields,
                first_page_size=100,
                next_page_size=100,
                max_pages=extra_pages_needed,  # fetch only what's needed
                include_total_on_first_page=False,
                sort=["@relevance", "LastUpdatePostDate:desc"],
            )
            # iterate_studies includes the first page internally, so we need to skip it
            # Our list_studies() call already fetched the first page; add subsequent pages only.
            if len(pages) > 1:
                studies_pages.extend(pages[1:])

    studies: List[Dict[str, Any]] = []
    for pg in studies_pages:
        studies.extend(pg.get("studies") or [])

    def _get_first(v):
        if isinstance(v, list):
            return v[0] if v else None
        return v

    out: List[Dict[str, Any]] = []
    for s in studies:
        # The 'fields' projection returns keys directly at the study level.
        nct_id = _get_first(s.get("NCTId"))
        title = _get_first(s.get("BriefTitle"))
        phase = _get_first(s.get("Phase"))
        status = _get_first(s.get("OverallStatus"))
        # Conditions / Interventions may be arrays in the projection
        conditions = s.get("Condition") or []
        if isinstance(conditions, str):
            conditions = [conditions]
        interventions = s.get("InterventionName") or []
        if isinstance(interventions, str):
            interventions = [interventions]
        sponsor = _get_first(s.get("LeadSponsorName"))

        if nct_id and title:
            out.append({
                "nct_id": nct_id,
                "title": title,
                "phase": phase,
                "status": status,
                "conditions": conditions,
                "interventions": interventions,
                "sponsor": sponsor,
            })

        if len(out) >= limit:
            break

    return out


def estimate_incidence(disease: str, region: str = "US", *, naaccr_version: str = "22", pages: int = 1) -> Dict[str, Any]:
    """
    Map a disease indication to a NAACCR Data Dictionary item using GET /data_item/{naaccr_version}/.
    Note: The NAACCR Data Dictionary API provides metadata about data items (not incidence counts).
    We return incidence_per_year=None and record the matched item in the 'source' string for traceability.
    """
    client = NAACCRClient()
    try:
        items = search_data_items(
            client,
            naaccr_version,
            q=disease,
            minimize_results=True,
            pages=max(1, pages),
            delay=0.25,
        )
    except Exception:
        items = []

    best = None
    if isinstance(items, list) and items:
        # Prefer items whose ItemName contains the disease term
        target = disease.lower()
        for it in items:
            name = str(it.get("ItemName") or "").lower()
            if target in name:
                best = it
                break
        if best is None:
            best = items[0]

    source = "NAACCR"
    if best:
        xml_id = best.get("XmlNaaccrId")
        item_no = best.get("ItemNumber")
        name = best.get("ItemName")
        source = f"NAACCR v{naaccr_version} item {item_no} ({xml_id}): {name}"

    return {"disease": disease, "region": region, "incidence_per_year": None, "source": source}


def search_patents_by_assignee(assignee: str, limit: int = 50) -> List[Dict[str, Any]]:
    return [
        {"number": "US-10,123,456-B2", "title": "Antibodies to target X",
         "filing_date": "2017-05-10", "issue_date": "2020-08-18",
         "ipc": ["C07K16/28"], "assignee": assignee}
    ]


def lookup_substances_by_company(company: str) -> List[Dict[str, Any]]:
    return [
        {"name": "Examplemab", "synonyms": ["EXMAB"], "cid": 424242}
    ]

# --- Data classes ---
@dataclass
class DrugRecord:
    brand_name: Optional[str]
    active_ingredient: Optional[str]
    application: Optional[str]
    approval_date: Optional[str]
    indications: List[str]


@dataclass
class TrialRecord:
    nct_id: str
    title: str
    phase: Optional[str]
    status: Optional[str]
    conditions: List[str]
    interventions: List[str]
    sponsor: Optional[str]


@dataclass
class PatentRecord:
    number: str
    title: str
    filing_date: Optional[str]
    issue_date: Optional[str]
    ipc: List[str]
    assignee: Optional[str]


@dataclass
class PopulationRecord:
    disease: str
    region: str
    incidence_per_year: Optional[int]
    source: Optional[str]


@dataclass
class CompanyIntel:
    company: str
    drugs_approved: List[DrugRecord]
    in_trials: List[TrialRecord]
    populations: List[PopulationRecord]
    patents: List[PatentRecord]
    competitors: List[str]

    def dict(self) -> Dict[str, Any]:
        return {
            "company": self.company,
            "drugs_approved": [asdict(d) for d in self.drugs_approved],
            "in_trials": [asdict(t) for t in self.in_trials],
            "populations": [asdict(p) for p in self.populations],
            "patents": [asdict(pt) for pt in self.patents],
            "competitors": self.competitors,
        }


# --- Heuristics ---

def infer_indications_from_drugs(drugs: List[DrugRecord]) -> List[str]:
    inds: List[str] = []
    for d in drugs:
        for ind in d.indications:
            if ind and ind not in inds:
                inds.append(ind)
    return inds


def infer_competitors(trials: List[TrialRecord], company: str) -> List[str]:
    competitors = set()
    for t in trials:
        s = (t.sponsor or "").strip()
        if s and company.lower() not in s.lower():
            competitors.add(s)
    return sorted(list(competitors))


# --- Public orchestration API ---

def build_company_intel(company: str, *, trial_limit: int = 50) -> CompanyIntel:
    # 1) Approved drugs (OpenFDA)
    raw_drugs = get_drug_approvals_for_sponsor(company)
    drugs = [
        DrugRecord(
            brand_name=d.get("brand_name"),
            active_ingredient=d.get("active_ingredient"),
            application=d.get("application"),
            approval_date=d.get("approval_date"),
            indications=d.get("indications") or [],
        )
        for d in raw_drugs
    ]

    # 2) Trials (ClinicalTrials.gov)
    raw_trials = search_studies(company, drugs, limit=trial_limit)
    trials = [
        TrialRecord(
            nct_id=t.get("nct_id"),
            title=t.get("title"),
            phase=t.get("phase"),
            status=t.get("status"),
            conditions=t.get("conditions") or [],
            interventions=t.get("interventions") or [],
            sponsor=t.get("sponsor"),
        )
        for t in raw_trials
    ]

    # 3) Population sizing (NAACCR – for oncology indications)
    indications = infer_indications_from_drugs(drugs)
    pops: List[PopulationRecord] = []
    for ind in indications:
        if any(k in ind.lower() for k in ["cancer", "carcinoma", "lymphoma", "leukemia"]):
            est = estimate_incidence(ind, region="US")
            pops.append(PopulationRecord(**est))

    # 4) Patents (USPTO ODP)
    raw_patents = search_patents_by_assignee(company)
    patents = [
        PatentRecord(
            number=p.get("number"), title=p.get("title"),
            filing_date=p.get("filing_date"), issue_date=p.get("issue_date"),
            ipc=p.get("ipc") or [], assignee=p.get("assignee")
        ) for p in raw_patents
    ]

    # 5) Competitors (naive: other trial sponsors in same query)
    competitors = infer_competitors(trials, company)

    return CompanyIntel(
        company=company,
        drugs_approved=drugs,
        in_trials=trials,
        populations=pops,
        patents=patents,
        competitors=competitors,
    )