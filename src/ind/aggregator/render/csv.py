import csv
from pathlib import Path

def _write_csv_rows(rows: list[dict], output_csv: Path, preferred: list[str]) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    keys: list[str] = []
    seen = set()
    for k in preferred:
        if any(k in (d or {}) for d in rows):
            keys.append(k)
            seen.add(k)
    for d in rows:
        for k in (d or {}).keys():
            if k not in seen:
                keys.append(k)
                seen.add(k)

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for d in rows:
            w.writerow({k: (d.get(k, "") if isinstance(d, dict) else "") for k in keys})


def _write_drugs_csv(drugs: list[dict], output_csv: Path) -> None:
    preferred = [
        "brand_name",
        "active_ingredient",
        "dosage_form",
        "route",
        "marketing_status",
        "application",
        "product_no",
        "approval_date",
        "sponsor",
    ]
    _write_csv_rows(drugs, output_csv, preferred)

def _write_ndc_csv(ndc_rows: list[dict], output_csv: Path) -> None:
    preferred = [
        "product_ndc",
        "brand_name",
        "generic_name",
        "labeler_name",
        "manufacturer_name",
        "dosage_form",
        "route",
        "marketing_category",
        "product_type",
        "finished",
        "listing_expiration_date",
    ]
    _write_csv_rows(ndc_rows, output_csv, preferred)

def _write_adverse_events_csv(rows: list[dict], output_csv: Path) -> None:
    preferred = [
        "safetyreportid",
        "receivedate",
        "receiptdate",
        "serious",
        "patientsex",
        "patientagegroup",
        "medicinalproduct",
        "manufacturer_name",
        "reaction_pt",
    ]
    _write_csv_rows(rows, output_csv, preferred)

def _write_enforcements_csv(rows: list[dict], output_csv: Path) -> None:
    preferred = [
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
    _write_csv_rows(rows, output_csv, preferred)

def _write_labels_csv(rows: list[dict], output_csv: Path) -> None:
    preferred = [
        "id","set_id","effective_time","version",
        "brand_name","generic_name","manufacturer_name",
        "product_ndc","package_ndc","route","dosage_form",
        "application_number","spl_id","spl_set_id",
    ]
    _write_csv_rows(rows, output_csv, preferred)

def _write_shortages_csv(rows: list[dict], output_csv: Path) -> None:
    preferred = [
        "package_ndc",
        "generic_name",
        "proprietary_name",
        "company_name",
        "status",
        "availability",
        "shortage_reason",
        "dosage_form",
        "strength",
        "therapeutic_category",
        "presentation",
        "update_type",
        "update_date",
        "initial_posting_date",
        "change_date",
        "discontinued_date",
        "resolved_note",
        "related_info",
        "related_info_link",
        "manufacturer_name",
    ]
    _write_csv_rows(rows, output_csv, preferred)

def _write_devices_csv(devices: list[dict], output_csv: Path) -> None:
    preferred = [
        "device_type",
        "k_number",
        "pma_number",
        "device_name",
        "trade_name",
        "generic_name",
        "applicant",
        "manufacturer_name",
        "product_code",
        "advisory_committee",
        "clearance_type",
        "decision_code",
        "decision_date",
    ]
    _write_csv_rows(devices, output_csv, preferred)

def _write_device_events_csv(rows: list[dict], output_csv: Path) -> None:
    preferred = [
        "mdr_report_key",
        "report_number",
        "date_received",
        "date_of_event",
        "report_date",
        "event_type",
        "manufacturer_name",
        "brand_name",
        "generic_name",
        "product_code",
        "product_problem_flag",
        "adverse_event_flag",
        "product_problem_text",
        "patient_problem_text",
    ]
    _write_csv_rows(rows, output_csv, preferred)

def _write_device_enforcements_csv(rows: list[dict], output_csv: Path) -> None:
        preferred = [
            "recall_number",
            "classification",
            "status",
            "report_date",
            "recall_initiation_date",
            "center_classification_date",
            "termination_date",
            "recalling_firm",
            "product_description",
            "reason_for_recall",
            "product_code",
            "product_type",
            "distribution_pattern",
            "code_info",
            "city",
            "state",
            "country",
            "voluntary_mandated",
            "event_id",
        ]
        _write_csv_rows(rows, output_csv, preferred)

def _write_device_recalls_csv(rows: list[dict], output_csv: Path) -> None:
    preferred = [
        "recall_number",
        "status",
        "report_date",
        "recall_initiation_date",
        "termination_date",
        "recalling_firm",
        "product_description",
        "reason_for_recall",
        "product_code",
        "product_type",
        "distribution_pattern",
        "code_info",
        "city",
        "state",
        "country",
        "voluntary_mandated",
        "event_id",
    ]
    _write_csv_rows(rows, output_csv, preferred)

def _write_device_registrationlisting_csv(rows: list[dict], output_csv: Path) -> None:
    preferred = [
        "registration_number","fei_number","registration_status_code",
        "initial_importer_flag","reg_expiry_date_year",
        "facility_name","facility_city","facility_state_code","facility_iso_country_code",
        "owner_operator_number","owner_operator_firm_name",
        "owner_operator_city","owner_operator_state_code","owner_operator_iso_country_code",
        "us_agent_name","us_agent_business_name","us_agent_city","us_agent_state_code","us_agent_iso_country_code",
        "establishment_type","proprietary_name",
        "product_code","k_number","pma_number","exempt",
        "device_class","medical_specialty_description","regulation_number",
    ]
    _write_csv_rows(rows, output_csv, preferred)

def _write_transparency_crl_csv(rows: list[dict], output_csv: Path) -> None:
    preferred = [
        "letter_date",
        "letter_type",
        "application_number",
        "approval_name",
        "approval_title",
        "approval_center",
        "company_name",
        "company_rep",
        "company_address",
        "file_name",
    ]
    _write_csv_rows(rows, output_csv, preferred)