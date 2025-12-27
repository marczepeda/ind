from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, List

from .sources.openfda import (_search_sponsor, _search_ndc_directory, _search_drug_adverse_events, _search_drug_enforcements, _search_drug_shortages, _search_drug_labels,
                             _flatten_approved_drugs, _flatten_ndc_directory, _flatten_drug_adverse_events, _flatten_drug_enforcements, _flatten_drug_shortages, _flatten_drug_labels,
                             _search_device_510k, _search_device_pma, _search_device_adverse_events, _search_device_enforcements, _search_device_recalls, _search_device_registrationlisting,
                             _flatten_510k, _flatten_pma, _flatten_device_adverse_events, _flatten_device_enforcements, _flatten_device_recalls, _flatten_device_registrationlisting,
                             _search_transparency_crl, _flatten_transparency_crl)

@dataclass
class CompanyOpenFDAIntel:
    company: str
    drugs_approved: List[Dict[str, Any]]
    ndc_directory: List[Dict[str, Any]]
    drug_adverse_events: List[Dict[str, Any]]
    drug_enforcements: List[Dict[str, Any]]
    drug_labels: List[Dict[str, Any]]
    drug_shortages: List[Dict[str, Any]]
    devices_510k: List[Dict[str, Any]]
    devices_pma: List[Dict[str, Any]]
    device_adverse_events: List[Dict[str, Any]]
    device_enforcements: List[Dict[str, Any]]
    device_recalls: List[Dict[str, Any]]
    device_registrationlisting: List[Dict[str, Any]]
    transparency_crl: List[Dict[str, Any]]

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

    device_event_records = _search_device_adverse_events(company, limit=max_records)
    device_adverse_events = _flatten_device_adverse_events(device_event_records)

    dev_enf_records = _search_device_enforcements(company, limit=max_records)
    device_enforcements = _flatten_device_enforcements(dev_enf_records)

    dev_recall_records = _search_device_recalls(company, limit=max_records)
    device_recalls = _flatten_device_recalls(dev_recall_records)

    reglist_records = _search_device_registrationlisting(company, limit=max_records)
    device_registrationlisting = _flatten_device_registrationlisting(reglist_records)

    crl_records = _search_transparency_crl(company, limit=max_records)
    transparency_crl = _flatten_transparency_crl(crl_records)

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
        device_adverse_events=device_adverse_events,
        device_enforcements=device_enforcements,
        device_recalls=device_recalls,
        device_registrationlisting=device_registrationlisting,
        transparency_crl=transparency_crl,
    )