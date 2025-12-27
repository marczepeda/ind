def _render_html(
    data: dict,
    icon_href: str,
    *,
    show_drug_approved: bool = False,
    show_drug_ndc: bool = False,
    show_drug_adverse_events: bool = False,
    show_drug_enforcements: bool = False,
    show_drug_labels: bool = False,
    show_drug_shortages: bool = False,
    show_device_approved: bool = False,
    show_device_adverse_events: bool = False,
    show_device_enforcements: bool = False,
    show_device_recalls: bool = False,
    show_device_registrationlisting: bool = False,
    show_transparency_crl: bool = False,
) -> str:
    # Minimal standalone HTML (no server). Style kept compact.
    def esc(s):
        return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # Build rows with data attributes for client-side filtering
    drugs_rows = "\n".join(
        f"<tr>"
        f"<td data-col='brand_name'>{esc(str(d.get('brand_name','')))}</td>"
        f"<td data-col='active_ingredient'>{esc(str(d.get('active_ingredient','')))}</td>"
        f"<td data-col='dosage_form'>{esc(str(d.get('dosage_form','')))}</td>"
        f"<td data-col='route'>{esc(str(d.get('route','')))}</td>"
        f"<td data-col='marketing_status'>{esc(str(d.get('marketing_status','')))}</td>"
        f"<td data-col='application'>{esc(str(d.get('application','')))}</td>"
        f"<td data-col='product_no'>{esc(str(d.get('product_no','')))}</td>"
        f"</tr>"
        for d in (data.get("drugs_approved") or [])
    ) or "<tr><td colspan=7>(none)</td></tr>"

    ndc_rows = "\n".join(
    f"<tr>"
    f"<td data-col='product_ndc'>{esc(str(d.get('product_ndc','')))}</td>"
    f"<td data-col='brand_name'>{esc(str(d.get('brand_name','')))}</td>"
    f"<td data-col='generic_name'>{esc(str(d.get('generic_name','')))}</td>"
    f"<td data-col='labeler_name'>{esc(str(d.get('labeler_name','')))}</td>"
    f"<td data-col='manufacturer_name'>{esc(str(d.get('manufacturer_name','')))}</td>"
    f"<td data-col='dosage_form'>{esc(str(d.get('dosage_form','')))}</td>"
    f"<td data-col='route'>{esc(str(d.get('route','')))}</td>"
    f"<td data-col='marketing_category'>{esc(str(d.get('marketing_category','')))}</td>"
    f"<td data-col='product_type'>{esc(str(d.get('product_type','')))}</td>"
    f"<td data-col='finished'>{esc(str(d.get('finished','')))}</td>"
    f"<td data-col='listing_expiration_date'>{esc(str(d.get('listing_expiration_date','')))}</td>"
    f"</tr>"
    for d in (data.get("ndc_directory") or [])
) or "<tr><td colspan=11>(none)</td></tr>"

    adverse_rows = "\n".join(
        f"<tr>"
        f"<td data-col='safetyreportid'>{esc(str(d.get('safetyreportid','')))}</td>"
        f"<td data-col='receivedate'>{esc(str(d.get('receivedate','')))}</td>"
        f"<td data-col='receiptdate'>{esc(str(d.get('receiptdate','')))}</td>"
        f"<td data-col='serious'>{esc(str(d.get('serious','')))}</td>"
        f"<td data-col='patientsex'>{esc(str(d.get('patientsex','')))}</td>"
        f"<td data-col='patientagegroup'>{esc(str(d.get('patientagegroup','')))}</td>"
        f"<td data-col='medicinalproduct'>{esc(str(d.get('medicinalproduct','')))}</td>"
        f"<td data-col='manufacturer_name'>{esc(str(d.get('manufacturer_name','')))}</td>"
        f"<td data-col='reaction_pt'>{esc(str(d.get('reaction_pt','')))}</td>"
        f"</tr>"
        for d in (data.get("drug_adverse_events") or [])
    ) or "<tr><td colspan=9>(none)</td></tr>"

    enforcement_rows = "\n".join(
        f"<tr>"
        f"<td data-col='recall_number'>{esc(str(d.get('recall_number','')))}</td>"
        f"<td data-col='classification'>{esc(str(d.get('classification','')))}</td>"
        f"<td data-col='status'>{esc(str(d.get('status','')))}</td>"
        f"<td data-col='report_date'>{esc(str(d.get('report_date','')))}</td>"
        f"<td data-col='recall_initiation_date'>{esc(str(d.get('recall_initiation_date','')))}</td>"
        f"<td data-col='termination_date'>{esc(str(d.get('termination_date','')))}</td>"
        f"<td data-col='recalling_firm'>{esc(str(d.get('recalling_firm','')))}</td>"
        f"<td data-col='product_description'>{esc(str(d.get('product_description','')))}</td>"
        f"<td data-col='reason_for_recall'>{esc(str(d.get('reason_for_recall','')))}</td>"
        f"<td data-col='distribution_pattern'>{esc(str(d.get('distribution_pattern','')))}</td>"
        f"<td data-col='code_info'>{esc(str(d.get('code_info','')))}</td>"
        f"<td data-col='city'>{esc(str(d.get('city','')))}</td>"
        f"<td data-col='state'>{esc(str(d.get('state','')))}</td>"
        f"<td data-col='country'>{esc(str(d.get('country','')))}</td>"
        f"</tr>"
        for d in (data.get("drug_enforcements") or [])
    ) or "<tr><td colspan=14>(none)</td></tr>"

    label_rows = "\n".join(
        f"<tr>"
        f"<td data-col='set_id'>{esc(str(d.get('set_id','')))}</td>"
        f"<td data-col='effective_time'>{esc(str(d.get('effective_time','')))}</td>"
        f"<td data-col='brand_name'>{esc(str(d.get('brand_name','')))}</td>"
        f"<td data-col='generic_name'>{esc(str(d.get('generic_name','')))}</td>"
        f"<td data-col='manufacturer_name'>{esc(str(d.get('manufacturer_name','')))}</td>"
        f"<td data-col='product_ndc'>{esc(str(d.get('product_ndc','')))}</td>"
        f"<td data-col='package_ndc'>{esc(str(d.get('package_ndc','')))}</td>"
        f"<td data-col='route'>{esc(str(d.get('route','')))}</td>"
        f"<td data-col='dosage_form'>{esc(str(d.get('dosage_form','')))}</td>"
        f"<td data-col='application_number'>{esc(str(d.get('application_number','')))}</td>"
        f"</tr>"
        for d in (data.get("drug_labels") or [])
    ) or "<tr><td colspan=10>(none)</td></tr>"

    shortages_rows = "\n".join(
        f"<tr>"
        f"<td data-col='package_ndc'>{esc(str(d.get('package_ndc','')))}</td>"
        f"<td data-col='generic_name'>{esc(str(d.get('generic_name','')))}</td>"
        f"<td data-col='proprietary_name'>{esc(str(d.get('proprietary_name','')))}</td>"
        f"<td data-col='company_name'>{esc(str(d.get('company_name','')))}</td>"
        f"<td data-col='status'>{esc(str(d.get('status','')))}</td>"
        f"<td data-col='availability'>{esc(str(d.get('availability','')))}</td>"
        f"<td data-col='shortage_reason'>{esc(str(d.get('shortage_reason','')))}</td>"
        f"<td data-col='dosage_form'>{esc(str(d.get('dosage_form','')))}</td>"
        f"<td data-col='strength'>{esc(str(d.get('strength','')))}</td>"
        f"<td data-col='therapeutic_category'>{esc(str(d.get('therapeutic_category','')))}</td>"
        f"<td data-col='update_date'>{esc(str(d.get('update_date','')))}</td>"
        f"<td data-col='initial_posting_date'>{esc(str(d.get('initial_posting_date','')))}</td>"
        f"</tr>"
        for d in (data.get("drug_shortages") or [])
    ) or "<tr><td colspan=12>(none)</td></tr>"

    devices_510k = data.get("devices_510k") or []
    devices_pma = data.get("devices_pma") or []

    devices_rows_510k = [
        (
            f"<tr>"
            f"<td data-col='device_type'>510k</td>"
            f"<td data-col='k_number'>{esc(str(d.get('k_number','')))}</td>"
            f"<td data-col='pma_number'></td>"
            f"<td data-col='device_name'>{esc(str(d.get('device_name','')))}</td>"
            f"<td data-col='trade_name'></td>"
            f"<td data-col='generic_name'></td>"
            f"<td data-col='applicant'>{esc(str(d.get('applicant','')))}</td>"
            f"<td data-col='manufacturer_name'>{esc(str(d.get('manufacturer_name','')))}</td>"
            f"<td data-col='product_code'>{esc(str(d.get('product_code','')))}</td>"
            f"<td data-col='advisory_committee'>{esc(str(d.get('advisory_committee','')))}</td>"
            f"<td data-col='clearance_type'>{esc(str(d.get('clearance_type','')))}</td>"
            f"<td data-col='decision_code'>{esc(str(d.get('decision_code','')))}</td>"
            f"<td data-col='decision_date'>{esc(str(d.get('decision_date','')))}</td>"
            f"</tr>"
        )
        for d in devices_510k
    ]

    devices_rows_pma = [
        (
            f"<tr>"
            f"<td data-col='device_type'>PMA</td>"
            f"<td data-col='k_number'></td>"
            f"<td data-col='pma_number'>{esc(str(d.get('pma_number','')))}</td>"
            f"<td data-col='device_name'></td>"
            f"<td data-col='trade_name'>{esc(str(d.get('trade_name','')))}</td>"
            f"<td data-col='generic_name'>{esc(str(d.get('generic_name','')))}</td>"
            f"<td data-col='applicant'>{esc(str(d.get('applicant','')))}</td>"
            f"<td data-col='manufacturer_name'>{esc(str(d.get('manufacturer_name','')))}</td>"
            f"<td data-col='product_code'>{esc(str(d.get('product_code','')))}</td>"
            f"<td data-col='advisory_committee'>{esc(str(d.get('advisory_committee','')))}</td>"
            f"<td data-col='clearance_type'></td>"
            f"<td data-col='decision_code'>{esc(str(d.get('decision_code','')))}</td>"
            f"<td data-col='decision_date'>{esc(str(d.get('decision_date','')))}</td>"
            f"</tr>"
        )
        for d in devices_pma
    ]

    devices_rows = "\n".join(devices_rows_510k + devices_rows_pma)
    if not devices_rows:
        devices_rows = "<tr><td colspan=13>(none)</td></tr>"

    device_event_rows = "\n".join(
        f"<tr>"
        f"<td data-col='mdr_report_key'>{esc(str(d.get('mdr_report_key','')))}</td>"
        f"<td data-col='report_number'>{esc(str(d.get('report_number','')))}</td>"
        f"<td data-col='date_received'>{esc(str(d.get('date_received','')))}</td>"
        f"<td data-col='date_of_event'>{esc(str(d.get('date_of_event','')))}</td>"
        f"<td data-col='report_date'>{esc(str(d.get('report_date','')))}</td>"
        f"<td data-col='event_type'>{esc(str(d.get('event_type','')))}</td>"
        f"<td data-col='manufacturer_name'>{esc(str(d.get('manufacturer_name','')))}</td>"
        f"<td data-col='brand_name'>{esc(str(d.get('brand_name','')))}</td>"
        f"<td data-col='generic_name'>{esc(str(d.get('generic_name','')))}</td>"
        f"<td data-col='product_code'>{esc(str(d.get('product_code','')))}</td>"
        f"<td data-col='product_problem_flag'>{esc(str(d.get('product_problem_flag','')))}</td>"
        f"<td data-col='adverse_event_flag'>{esc(str(d.get('adverse_event_flag','')))}</td>"
        f"<td data-col='product_problem_text'>{esc(str(d.get('product_problem_text','')))}</td>"
        f"<td data-col='patient_problem_text'>{esc(str(d.get('patient_problem_text','')))}</td>"
        f"</tr>"
        for d in (data.get("device_adverse_events") or [])
    ) or "<tr><td colspan=14>(none)</td></tr>"

    device_enforcement_rows = "\n".join(
        f"<tr>"
        f"<td data-col='recall_number'>{esc(str(d.get('recall_number','')))}</td>"
        f"<td data-col='classification'>{esc(str(d.get('classification','')))}</td>"
        f"<td data-col='status'>{esc(str(d.get('status','')))}</td>"
        f"<td data-col='report_date'>{esc(str(d.get('report_date','')))}</td>"
        f"<td data-col='recall_initiation_date'>{esc(str(d.get('recall_initiation_date','')))}</td>"
        f"<td data-col='center_classification_date'>{esc(str(d.get('center_classification_date','')))}</td>"
        f"<td data-col='termination_date'>{esc(str(d.get('termination_date','')))}</td>"
        f"<td data-col='recalling_firm'>{esc(str(d.get('recalling_firm','')))}</td>"
        f"<td data-col='product_description'>{esc(str(d.get('product_description','')))}</td>"
        f"<td data-col='reason_for_recall'>{esc(str(d.get('reason_for_recall','')))}</td>"
        f"<td data-col='product_code'>{esc(str(d.get('product_code','')))}</td>"
        f"<td data-col='product_type'>{esc(str(d.get('product_type','')))}</td>"
        f"<td data-col='distribution_pattern'>{esc(str(d.get('distribution_pattern','')))}</td>"
        f"<td data-col='code_info'>{esc(str(d.get('code_info','')))}</td>"
        f"<td data-col='city'>{esc(str(d.get('city','')))}</td>"
        f"<td data-col='state'>{esc(str(d.get('state','')))}</td>"
        f"<td data-col='country'>{esc(str(d.get('country','')))}</td>"
        f"<td data-col='voluntary_mandated'>{esc(str(d.get('voluntary_mandated','')))}</td>"
        f"<td data-col='event_id'>{esc(str(d.get('event_id','')))}</td>"
        f"</tr>"
        for d in (data.get("device_enforcements") or [])
    ) or "<tr><td colspan=19>(none)</td></tr>"

    device_recall_rows = "\n".join(
        f"<tr>"
        f"<td data-col='recall_number'>{esc(str(d.get('recall_number','')))}</td>"
        f"<td data-col='status'>{esc(str(d.get('status','')))}</td>"
        f"<td data-col='report_date'>{esc(str(d.get('report_date','')))}</td>"
        f"<td data-col='recall_initiation_date'>{esc(str(d.get('recall_initiation_date','')))}</td>"
        f"<td data-col='termination_date'>{esc(str(d.get('termination_date','')))}</td>"
        f"<td data-col='recalling_firm'>{esc(str(d.get('recalling_firm','')))}</td>"
        f"<td data-col='product_description'>{esc(str(d.get('product_description','')))}</td>"
        f"<td data-col='reason_for_recall'>{esc(str(d.get('reason_for_recall','')))}</td>"
        f"<td data-col='product_code'>{esc(str(d.get('product_code','')))}</td>"
        f"<td data-col='product_type'>{esc(str(d.get('product_type','')))}</td>"
        f"<td data-col='distribution_pattern'>{esc(str(d.get('distribution_pattern','')))}</td>"
        f"<td data-col='code_info'>{esc(str(d.get('code_info','')))}</td>"
        f"<td data-col='city'>{esc(str(d.get('city','')))}</td>"
        f"<td data-col='state'>{esc(str(d.get('state','')))}</td>"
        f"<td data-col='country'>{esc(str(d.get('country','')))}</td>"
        f"<td data-col='voluntary_mandated'>{esc(str(d.get('voluntary_mandated','')))}</td>"
        f"<td data-col='event_id'>{esc(str(d.get('event_id','')))}</td>"
        f"</tr>"
        for d in (data.get("device_recalls") or [])
    ) or "<tr><td colspan=17>(none)</td></tr>"

    device_reglist_rows = "\n".join(
        f"<tr>"
        f"<td data-col='registration_number'>{esc(str(d.get('registration_number','')))}</td>"
        f"<td data-col='fei_number'>{esc(str(d.get('fei_number','')))}</td>"
        f"<td data-col='registration_status_code'>{esc(str(d.get('registration_status_code','')))}</td>"
        f"<td data-col='facility_name'>{esc(str(d.get('facility_name','')))}</td>"
        f"<td data-col='facility_city'>{esc(str(d.get('facility_city','')))}</td>"
        f"<td data-col='facility_state_code'>{esc(str(d.get('facility_state_code','')))}</td>"
        f"<td data-col='facility_iso_country_code'>{esc(str(d.get('facility_iso_country_code','')))}</td>"
        f"<td data-col='owner_operator_number'>{esc(str(d.get('owner_operator_number','')))}</td>"
        f"<td data-col='owner_operator_firm_name'>{esc(str(d.get('owner_operator_firm_name','')))}</td>"
        f"<td data-col='establishment_type'>{esc(str(d.get('establishment_type','')))}</td>"
        f"<td data-col='proprietary_name'>{esc(str(d.get('proprietary_name','')))}</td>"
        f"<td data-col='product_code'>{esc(str(d.get('product_code','')))}</td>"
        f"<td data-col='k_number'>{esc(str(d.get('k_number','')))}</td>"
        f"<td data-col='pma_number'>{esc(str(d.get('pma_number','')))}</td>"
        f"<td data-col='device_class'>{esc(str(d.get('device_class','')))}</td>"
        f"<td data-col='regulation_number'>{esc(str(d.get('regulation_number','')))}</td>"
        f"</tr>"
        for d in (data.get("device_registrationlisting") or [])
    ) or "<tr><td colspan=16>(none)</td></tr>"

    transparency_crl_rows = "\n".join(
        f"<tr>"
        f"<td data-col='letter_date'>{esc(str(d.get('letter_date','')))}</td>"
        f"<td data-col='letter_type'>{esc(str(d.get('letter_type','')))}</td>"
        f"<td data-col='application_number'>{esc(str(d.get('application_number','')))}</td>"
        f"<td data-col='approval_name'>{esc(str(d.get('approval_name','')))}</td>"
        f"<td data-col='approval_center'>{esc(str(d.get('approval_center','')))}</td>"
        f"<td data-col='company_name'>{esc(str(d.get('company_name','')))}</td>"
        f"<td data-col='file_name'>{esc(str(d.get('file_name','')))}</td>"
        f"</tr>"
        for d in (data.get("transparency_crl") or [])
    ) or "<tr><td colspan=7>(none)</td></tr>"

    company_esc = esc(data.get('company', ''))

    drug_card = """
  <div class="card">
    <h3 class="title">openFDA: Approved Drugs</h3>
    <table id="drugs-table">
      <thead>
        <tr>
          <th data-sort="brand_name" title="Click to sort">Brand</th>
          <th data-sort="active_ingredient" title="Click to sort">Ingredient</th>
          <th data-sort="dosage_form" title="Click to sort">Dosage Form</th>
          <th data-sort="route" title="Click to sort">Route</th>
          <th data-sort="marketing_status" title="Click to sort">Marketing Status</th>
          <th data-sort="application" title="Click to sort">Application</th>
          <th data-sort="product_no" title="Click to sort">Product No</th>
        </tr>
        <tr class="filters">
          <th><select data-filter="brand_name"><option value="">All</option></select></th>
          <th><select data-filter="active_ingredient"><option value="">All</option></select></th>
          <th><select data-filter="dosage_form"><option value="">All</option></select></th>
          <th><select data-filter="route"><option value="">All</option></select></th>
          <th><select data-filter="marketing_status"><option value="">All</option></select></th>
          <th><select data-filter="application"><option value="">All</option></select></th>
          <th><select data-filter="product_no"><option value="">All</option></select></th>
        </tr>
      </thead>
      <tbody>__DRUGS_ROWS__</tbody>
    </table>
  </div>
"""

    ndc_card = """
  <div class=\"card\">
    <h3 class=\"title\">openFDA: NDC Directory</h3>
    <table id=\"ndc-table\">
      <thead>
        <tr>
          <th data-sort=\"product_ndc\" title=\"Click to sort\">Product NDC</th>
          <th data-sort=\"brand_name\" title=\"Click to sort\">Brand</th>
          <th data-sort=\"generic_name\" title=\"Click to sort\">Generic</th>
          <th data-sort=\"labeler_name\" title=\"Click to sort\">Labeler</th>
          <th data-sort=\"manufacturer_name\" title=\"Click to sort\">Manufacturer</th>
          <th data-sort=\"dosage_form\" title=\"Click to sort\">Dosage Form</th>
          <th data-sort=\"route\" title=\"Click to sort\">Route</th>
          <th data-sort=\"marketing_category\" title=\"Click to sort\">Marketing Category</th>
          <th data-sort=\"product_type\" title=\"Click to sort\">Product Type</th>
          <th data-sort=\"finished\" title=\"Click to sort\">Finished</th>
          <th data-sort=\"listing_expiration_date\" title=\"Click to sort\">Listing Expiration</th>
        </tr>
        <tr class=\"filters\">
          <th><select data-filter=\"product_ndc\"><option value=\"\">All</option></select></th>
          <th><select data-filter=\"brand_name\"><option value=\"\">All</option></select></th>
          <th><select data-filter=\"generic_name\"><option value=\"\">All</option></select></th>
          <th><select data-filter=\"labeler_name\"><option value=\"\">All</option></select></th>
          <th><select data-filter=\"manufacturer_name\"><option value=\"\">All</option></select></th>
          <th><select data-filter=\"dosage_form\"><option value=\"\">All</option></select></th>
          <th><select data-filter=\"route\"><option value=\"\">All</option></select></th>
          <th><select data-filter=\"marketing_category\"><option value=\"\">All</option></select></th>
          <th><select data-filter=\"product_type\"><option value=\"\">All</option></select></th>
          <th><select data-filter=\"finished\"><option value=\"\">All</option></select></th>
          <th><select data-filter=\"listing_expiration_date\"><option value=\"\">All</option></select></th>
        </tr>
      </thead>
      <tbody>__NDC_ROWS__</tbody>
    </table>
  </div>
"""

    adverse_card = """
  <div class=\"card\">
    <h3 class=\"title\">openFDA: Drug Adverse Events (FAERS)</h3>
    <table id=\"adverse-table\">
      <thead>
        <tr>
          <th data-sort=\"safetyreportid\" title=\"Click to sort\">Report ID</th>
          <th data-sort=\"receivedate\" title=\"Click to sort\">Receive Date</th>
          <th data-sort=\"receiptdate\" title=\"Click to sort\">Receipt Date</th>
          <th data-sort=\"serious\" title=\"Click to sort\">Serious</th>
          <th data-sort=\"patientsex\" title=\"Click to sort\">Sex</th>
          <th data-sort=\"patientagegroup\" title=\"Click to sort\">Age Group</th>
          <th data-sort=\"medicinalproduct\" title=\"Click to sort\">Medicinal Product</th>
          <th data-sort=\"manufacturer_name\" title=\"Click to sort\">Manufacturer</th>
          <th data-sort=\"reaction_pt\" title=\"Click to sort\">Reaction PT</th>
        </tr>
        <tr class=\"filters\">
          <th><select data-filter=\"safetyreportid\"><option value=\"\">All</option></select></th>
          <th><select data-filter=\"receivedate\"><option value=\"\">All</option></select></th>
          <th><select data-filter=\"receiptdate\"><option value=\"\">All</option></select></th>
          <th><select data-filter=\"serious\"><option value=\"\">All</option></select></th>
          <th><select data-filter=\"patientsex\"><option value=\"\">All</option></select></th>
          <th><select data-filter=\"patientagegroup\"><option value=\"\">All</option></select></th>
          <th><select data-filter=\"medicinalproduct\"><option value=\"\">All</option></select></th>
          <th><select data-filter=\"manufacturer_name\"><option value=\"\">All</option></select></th>
          <th><select data-filter=\"reaction_pt\"><option value=\"\">All</option></select></th>
        </tr>
      </thead>
      <tbody>__ADVERSE_ROWS__</tbody>
    </table>
  </div>
"""

    enforcement_card = """
  <div class="card">
    <h3 class="title">openFDA: Drug Enforcement Reports (Recalls)</h3>
    <table id="enforcement-table">
      <thead>
        <tr>
          <th data-sort="recall_number" title="Click to sort">Recall #</th>
          <th data-sort="classification" title="Click to sort">Class</th>
          <th data-sort="status" title="Click to sort">Status</th>
          <th data-sort="report_date" title="Click to sort">Report Date</th>
          <th data-sort="recall_initiation_date" title="Click to sort">Initiation</th>
          <th data-sort="termination_date" title="Click to sort">Termination</th>
          <th data-sort="recalling_firm" title="Click to sort">Recalling Firm</th>
          <th data-sort="product_description" title="Click to sort">Product</th>
          <th data-sort="reason_for_recall" title="Click to sort">Reason</th>
          <th data-sort="distribution_pattern" title="Click to sort">Distribution</th>
          <th data-sort="code_info" title="Click to sort">Code Info</th>
          <th data-sort="city" title="Click to sort">City</th>
          <th data-sort="state" title="Click to sort">State</th>
          <th data-sort="country" title="Click to sort">Country</th>
        </tr>
        <tr class="filters">
          <th><select data-filter="recall_number"><option value="">All</option></select></th>
          <th><select data-filter="classification"><option value="">All</option></select></th>
          <th><select data-filter="status"><option value="">All</option></select></th>
          <th><select data-filter="report_date"><option value="">All</option></select></th>
          <th><select data-filter="recall_initiation_date"><option value="">All</option></select></th>
          <th><select data-filter="termination_date"><option value="">All</option></select></th>
          <th><select data-filter="recalling_firm"><option value="">All</option></select></th>
          <th><select data-filter="product_description"><option value="">All</option></select></th>
          <th><select data-filter="reason_for_recall"><option value="">All</option></select></th>
          <th><select data-filter="distribution_pattern"><option value="">All</option></select></th>
          <th><select data-filter="code_info"><option value="">All</option></select></th>
          <th><select data-filter="city"><option value="">All</option></select></th>
          <th><select data-filter="state"><option value="">All</option></select></th>
          <th><select data-filter="country"><option value="">All</option></select></th>
        </tr>
      </thead>
      <tbody>__ENFORCEMENT_ROWS__</tbody>
    </table>
  </div>
"""

    label_card = """
    <div class="card">
        <h3 class="title">openFDA: Drug Product Labeling</h3>
        <table id="labels-table">
        <thead>
            <tr>
            <th data-sort="set_id">SPL Set ID</th>
            <th data-sort="effective_time">Effective Time</th>
            <th data-sort="brand_name">Brand</th>
            <th data-sort="generic_name">Generic</th>
            <th data-sort="manufacturer_name">Manufacturer</th>
            <th data-sort="product_ndc">Product NDC</th>
            <th data-sort="package_ndc">Package NDC</th>
            <th data-sort="route">Route</th>
            <th data-sort="dosage_form">Dosage Form</th>
            <th data-sort="application_number">Application #</th>
            </tr>
            <tr class="filters">
            <th><select data-filter="set_id"><option value="">All</option></select></th>
            <th><select data-filter="effective_time"><option value="">All</option></select></th>
            <th><select data-filter="brand_name"><option value="">All</option></select></th>
            <th><select data-filter="generic_name"><option value="">All</option></select></th>
            <th><select data-filter="manufacturer_name"><option value="">All</option></select></th>
            <th><select data-filter="product_ndc"><option value="">All</option></select></th>
            <th><select data-filter="package_ndc"><option value="">All</option></select></th>
            <th><select data-filter="route"><option value="">All</option></select></th>
            <th><select data-filter="dosage_form"><option value="">All</option></select></th>
            <th><select data-filter="application_number"><option value="">All</option></select></th>
            </tr>
        </thead>
        <tbody>__LABEL_ROWS__</tbody>
        </table>
    </div>
    """
    
    shortages_card = """
  <div class="card">
    <h3 class="title">openFDA: Drug Shortages</h3>
    <table id="shortages-table">
      <thead>
        <tr>
          <th data-sort="package_ndc" title="Click to sort">Package NDC</th>
          <th data-sort="generic_name" title="Click to sort">Generic</th>
          <th data-sort="proprietary_name" title="Click to sort">Proprietary</th>
          <th data-sort="company_name" title="Click to sort">Company</th>
          <th data-sort="status" title="Click to sort">Status</th>
          <th data-sort="availability" title="Click to sort">Availability</th>
          <th data-sort="shortage_reason" title="Click to sort">Reason</th>
          <th data-sort="dosage_form" title="Click to sort">Dosage Form</th>
          <th data-sort="strength" title="Click to sort">Strength</th>
          <th data-sort="therapeutic_category" title="Click to sort">Therapeutic Category</th>
          <th data-sort="update_date" title="Click to sort">Update Date</th>
          <th data-sort="initial_posting_date" title="Click to sort">Initial Posting</th>
        </tr>
        <tr class="filters">
          <th><select data-filter="package_ndc"><option value="">All</option></select></th>
          <th><select data-filter="generic_name"><option value="">All</option></select></th>
          <th><select data-filter="proprietary_name"><option value="">All</option></select></th>
          <th><select data-filter="company_name"><option value="">All</option></select></th>
          <th><select data-filter="status"><option value="">All</option></select></th>
          <th><select data-filter="availability"><option value="">All</option></select></th>
          <th><select data-filter="shortage_reason"><option value="">All</option></select></th>
          <th><select data-filter="dosage_form"><option value="">All</option></select></th>
          <th><select data-filter="strength"><option value="">All</option></select></th>
          <th><select data-filter="therapeutic_category"><option value="">All</option></select></th>
          <th><select data-filter="update_date"><option value="">All</option></select></th>
          <th><select data-filter="initial_posting_date"><option value="">All</option></select></th>
        </tr>
      </thead>
      <tbody>__SHORTAGES_ROWS__</tbody>
    </table>
  </div>
"""

    device_card = """
  <div class="card">
    <h3 class="title">openFDA: Approved / Cleared Medical Devices</h3>
    <table id="devices-table">
      <thead>
        <tr>
          <th data-sort="device_type" title="Click to sort">Type</th>
          <th data-sort="k_number" title="Click to sort">510(k)</th>
          <th data-sort="pma_number" title="Click to sort">PMA</th>
          <th data-sort="device_name" title="Click to sort">Device Name</th>
          <th data-sort="trade_name" title="Click to sort">Trade Name</th>
          <th data-sort="generic_name" title="Click to sort">Generic Name</th>
          <th data-sort="applicant" title="Click to sort">Applicant</th>
          <th data-sort="manufacturer_name" title="Click to sort">Manufacturer</th>
          <th data-sort="product_code" title="Click to sort">Product Code</th>
          <th data-sort="advisory_committee" title="Click to sort">Advisory</th>
          <th data-sort="clearance_type" title="Click to sort">Clearance</th>
          <th data-sort="decision_code" title="Click to sort">Decision</th>
          <th data-sort="decision_date" title="Click to sort">Decision Date</th>
        </tr>
        <tr class="filters">
          <th><select data-filter="device_type"><option value="">All</option></select></th>
          <th><select data-filter="k_number"><option value="">All</option></select></th>
          <th><select data-filter="pma_number"><option value="">All</option></select></th>
          <th><select data-filter="device_name"><option value="">All</option></select></th>
          <th><select data-filter="trade_name"><option value="">All</option></select></th>
          <th><select data-filter="generic_name"><option value="">All</option></select></th>
          <th><select data-filter="applicant"><option value="">All</option></select></th>
          <th><select data-filter="manufacturer_name"><option value="">All</option></select></th>
          <th><select data-filter="product_code"><option value="">All</option></select></th>
          <th><select data-filter="advisory_committee"><option value="">All</option></select></th>
          <th><select data-filter="clearance_type"><option value="">All</option></select></th>
          <th><select data-filter="decision_code"><option value="">All</option></select></th>
          <th><select data-filter="decision_date"><option value="">All</option></select></th>
        </tr>
      </thead>
      <tbody>__DEVICES_ROWS__</tbody>
    </table>
  </div>
"""

    device_event_card = """
  <div class="card">
    <h3 class="title">openFDA: Device Adverse Events (MDR)</h3>
    <table id="device-events-table">
      <thead>
        <tr>
          <th data-sort="mdr_report_key" title="Click to sort">MDR Key</th>
          <th data-sort="report_number" title="Click to sort">Report #</th>
          <th data-sort="date_received" title="Click to sort">Date Received</th>
          <th data-sort="date_of_event" title="Click to sort">Date of Event</th>
          <th data-sort="report_date" title="Click to sort">Report Date</th>
          <th data-sort="event_type" title="Click to sort">Event Type</th>
          <th data-sort="manufacturer_name" title="Click to sort">Manufacturer</th>
          <th data-sort="brand_name" title="Click to sort">Brand</th>
          <th data-sort="generic_name" title="Click to sort">Generic</th>
          <th data-sort="product_code" title="Click to sort">Product Code</th>
          <th data-sort="product_problem_flag" title="Click to sort">Prod Prob Flag</th>
          <th data-sort="adverse_event_flag" title="Click to sort">AE Flag</th>
          <th data-sort="product_problem_text" title="Click to sort">Product Problem</th>
          <th data-sort="patient_problem_text" title="Click to sort">Patient Problem</th>
        </tr>
        <tr class="filters">
          <th><select data-filter="mdr_report_key"><option value="">All</option></select></th>
          <th><select data-filter="report_number"><option value="">All</option></select></th>
          <th><select data-filter="date_received"><option value="">All</option></select></th>
          <th><select data-filter="date_of_event"><option value="">All</option></select></th>
          <th><select data-filter="report_date"><option value="">All</option></select></th>
          <th><select data-filter="event_type"><option value="">All</option></select></th>
          <th><select data-filter="manufacturer_name"><option value="">All</option></select></th>
          <th><select data-filter="brand_name"><option value="">All</option></select></th>
          <th><select data-filter="generic_name"><option value="">All</option></select></th>
          <th><select data-filter="product_code"><option value="">All</option></select></th>
          <th><select data-filter="product_problem_flag"><option value="">All</option></select></th>
          <th><select data-filter="adverse_event_flag"><option value="">All</option></select></th>
          <th><select data-filter="product_problem_text"><option value="">All</option></select></th>
          <th><select data-filter="patient_problem_text"><option value="">All</option></select></th>
        </tr>
      </thead>
      <tbody>__DEVICE_EVENT_ROWS__</tbody>
    </table>
  </div>
"""

    device_enforcement_card = """
  <div class="card">
    <h3 class="title">openFDA: Device Enforcement Reports (Recalls)</h3>
    <table id="device-enforcement-table">
      <thead>
        <tr>
          <th data-sort="recall_number" title="Click to sort">Recall #</th>
          <th data-sort="classification" title="Click to sort">Class</th>
          <th data-sort="status" title="Click to sort">Status</th>
          <th data-sort="report_date" title="Click to sort">Report Date</th>
          <th data-sort="recall_initiation_date" title="Click to sort">Initiation</th>
          <th data-sort="center_classification_date" title="Click to sort">Center Class Date</th>
          <th data-sort="termination_date" title="Click to sort">Termination</th>
          <th data-sort="recalling_firm" title="Click to sort">Recalling Firm</th>
          <th data-sort="product_description" title="Click to sort">Product</th>
          <th data-sort="reason_for_recall" title="Click to sort">Reason</th>
          <th data-sort="product_code" title="Click to sort">Product Code</th>
          <th data-sort="product_type" title="Click to sort">Product Type</th>
          <th data-sort="distribution_pattern" title="Click to sort">Distribution</th>
          <th data-sort="code_info" title="Click to sort">Code Info</th>
          <th data-sort="city" title="Click to sort">City</th>
          <th data-sort="state" title="Click to sort">State</th>
          <th data-sort="country" title="Click to sort">Country</th>
          <th data-sort="voluntary_mandated" title="Click to sort">Voluntary/Mandated</th>
          <th data-sort="event_id" title="Click to sort">Event ID</th>
        </tr>
        <tr class="filters">
          <th><select data-filter="recall_number"><option value="">All</option></select></th>
          <th><select data-filter="classification"><option value="">All</option></select></th>
          <th><select data-filter="status"><option value="">All</option></select></th>
          <th><select data-filter="report_date"><option value="">All</option></select></th>
          <th><select data-filter="recall_initiation_date"><option value="">All</option></select></th>
          <th><select data-filter="center_classification_date"><option value="">All</option></select></th>
          <th><select data-filter="termination_date"><option value="">All</option></select></th>
          <th><select data-filter="recalling_firm"><option value="">All</option></select></th>
          <th><select data-filter="product_description"><option value="">All</option></select></th>
          <th><select data-filter="reason_for_recall"><option value="">All</option></select></th>
          <th><select data-filter="product_code"><option value="">All</option></select></th>
          <th><select data-filter="product_type"><option value="">All</option></select></th>
          <th><select data-filter="distribution_pattern"><option value="">All</option></select></th>
          <th><select data-filter="code_info"><option value="">All</option></select></th>
          <th><select data-filter="city"><option value="">All</option></select></th>
          <th><select data-filter="state"><option value="">All</option></select></th>
          <th><select data-filter="country"><option value="">All</option></select></th>
          <th><select data-filter="voluntary_mandated"><option value="">All</option></select></th>
          <th><select data-filter="event_id"><option value="">All</option></select></th>
        </tr>
      </thead>
      <tbody>__DEVICE_ENFORCEMENT_ROWS__</tbody>
    </table>
  </div>
"""

    device_recall_card = """
  <div class="card">
    <h3 class="title">openFDA: Device Recall Reports</h3>
    <table id="device-recall-table">
      <thead>
        <tr>
          <th data-sort="recall_number" title="Click to sort">Recall #</th>
          <th data-sort="status" title="Click to sort">Status</th>
          <th data-sort="report_date" title="Click to sort">Report Date</th>
          <th data-sort="recall_initiation_date" title="Click to sort">Initiation</th>
          <th data-sort="termination_date" title="Click to sort">Termination</th>
          <th data-sort="recalling_firm" title="Click to sort">Recalling Firm</th>
          <th data-sort="product_description" title="Click to sort">Product</th>
          <th data-sort="reason_for_recall" title="Click to sort">Reason</th>
          <th data-sort="product_code" title="Click to sort">Product Code</th>
          <th data-sort="product_type" title="Click to sort">Product Type</th>
          <th data-sort="distribution_pattern" title="Click to sort">Distribution</th>
          <th data-sort="code_info" title="Click to sort">Code Info</th>
          <th data-sort="city" title="Click to sort">City</th>
          <th data-sort="state" title="Click to sort">State</th>
          <th data-sort="country" title="Click to sort">Country</th>
          <th data-sort="voluntary_mandated" title="Click to sort">Voluntary/Mandated</th>
          <th data-sort="event_id" title="Click to sort">Event ID</th>
        </tr>
        <tr class="filters">
          <th><select data-filter="recall_number"><option value="">All</option></select></th>
          <th><select data-filter="status"><option value="">All</option></select></th>
          <th><select data-filter="report_date"><option value="">All</option></select></th>
          <th><select data-filter="recall_initiation_date"><option value="">All</option></select></th>
          <th><select data-filter="termination_date"><option value="">All</option></select></th>
          <th><select data-filter="recalling_firm"><option value="">All</option></select></th>
          <th><select data-filter="product_description"><option value="">All</option></select></th>
          <th><select data-filter="reason_for_recall"><option value="">All</option></select></th>
          <th><select data-filter="product_code"><option value="">All</option></select></th>
          <th><select data-filter="product_type"><option value="">All</option></select></th>
          <th><select data-filter="distribution_pattern"><option value="">All</option></select></th>
          <th><select data-filter="code_info"><option value="">All</option></select></th>
          <th><select data-filter="city"><option value="">All</option></select></th>
          <th><select data-filter="state"><option value="">All</option></select></th>
          <th><select data-filter="country"><option value="">All</option></select></th>
          <th><select data-filter="voluntary_mandated"><option value="">All</option></select></th>
          <th><select data-filter="event_id"><option value="">All</option></select></th>
        </tr>
      </thead>
      <tbody>__DEVICE_RECALL_ROWS__</tbody>
    </table>
  </div>
"""

    device_reglist_card = """
  <div class="card">
    <h3 class="title">openFDA: Device Registration &amp; Listing</h3>
    <table id="device-reglist-table">
      <thead>
        <tr>
          <th data-sort="registration_number" title="Click to sort">Registration #</th>
          <th data-sort="fei_number" title="Click to sort">FEI</th>
          <th data-sort="registration_status_code" title="Click to sort">Status</th>
          <th data-sort="facility_name" title="Click to sort">Facility</th>
          <th data-sort="facility_city" title="Click to sort">City</th>
          <th data-sort="facility_state_code" title="Click to sort">State</th>
          <th data-sort="facility_iso_country_code" title="Click to sort">Country</th>
          <th data-sort="owner_operator_number" title="Click to sort">Owner Op #</th>
          <th data-sort="owner_operator_firm_name" title="Click to sort">Owner Operator</th>
          <th data-sort="establishment_type" title="Click to sort">Establishment Type</th>
          <th data-sort="proprietary_name" title="Click to sort">Proprietary Name</th>
          <th data-sort="product_code" title="Click to sort">Product Code(s)</th>
          <th data-sort="k_number" title="Click to sort">510(k)</th>
          <th data-sort="pma_number" title="Click to sort">PMA</th>
          <th data-sort="device_class" title="Click to sort">Class</th>
          <th data-sort="regulation_number" title="Click to sort">Regulation #</th>
        </tr>
        <tr class="filters">
          <th><select data-filter="registration_number"><option value="">All</option></select></th>
          <th><select data-filter="fei_number"><option value="">All</option></select></th>
          <th><select data-filter="registration_status_code"><option value="">All</option></select></th>
          <th><select data-filter="facility_name"><option value="">All</option></select></th>
          <th><select data-filter="facility_city"><option value="">All</option></select></th>
          <th><select data-filter="facility_state_code"><option value="">All</option></select></th>
          <th><select data-filter="facility_iso_country_code"><option value="">All</option></select></th>
          <th><select data-filter="owner_operator_number"><option value="">All</option></select></th>
          <th><select data-filter="owner_operator_firm_name"><option value="">All</option></select></th>
          <th><select data-filter="establishment_type"><option value="">All</option></select></th>
          <th><select data-filter="proprietary_name"><option value="">All</option></select></th>
          <th><select data-filter="product_code"><option value="">All</option></select></th>
          <th><select data-filter="k_number"><option value="">All</option></select></th>
          <th><select data-filter="pma_number"><option value="">All</option></select></th>
          <th><select data-filter="device_class"><option value="">All</option></select></th>
          <th><select data-filter="regulation_number"><option value="">All</option></select></th>
        </tr>
      </thead>
      <tbody>__DEVICE_REGLIST_ROWS__</tbody>
    </table>
  </div>
"""

    transparency_crl_card = """
  <div class="card">
    <h3 class="title">openFDA: Transparency – Complete Response Letters (CRL)</h3>
    <table id="transparency-crl-table">
      <thead>
        <tr>
          <th data-sort="letter_date" title="Click to sort">Letter Date</th>
          <th data-sort="letter_type" title="Click to sort">Letter Type</th>
          <th data-sort="application_number" title="Click to sort">Application #</th>
          <th data-sort="approval_name" title="Click to sort">Approval Name</th>
          <th data-sort="approval_center" title="Click to sort">Center</th>
          <th data-sort="company_name" title="Click to sort">Company</th>
          <th data-sort="file_name" title="Click to sort">File</th>
        </tr>
        <tr class="filters">
          <th><select data-filter="letter_date"><option value="">All</option></select></th>
          <th><select data-filter="letter_type"><option value="">All</option></select></th>
          <th><select data-filter="application_number"><option value="">All</option></select></th>
          <th><select data-filter="approval_name"><option value="">All</option></select></th>
          <th><select data-filter="approval_center"><option value="">All</option></select></th>
          <th><select data-filter="company_name"><option value="">All</option></select></th>
          <th><select data-filter="file_name"><option value="">All</option></select></th>
        </tr>
      </thead>
      <tbody>__TRANSPARENCY_CRL_ROWS__</tbody>
    </table>
  </div>
"""

    init_calls = []
    if show_drug_approved:
        init_calls.append("  initTable('drugs-table');")
    if show_drug_ndc:
        init_calls.append("  initTable('ndc-table');")
    if show_drug_adverse_events:
        init_calls.append("  initTable('adverse-table');")
    if show_drug_enforcements:
        init_calls.append("  initTable('enforcement-table');")
    if show_drug_labels:
        init_calls.append("  initTable('labels-table');")
    if show_drug_shortages:
        init_calls.append("  initTable('shortages-table');")
    if show_device_approved:
        init_calls.append("  initTable('devices-table');")
    if show_device_adverse_events:
        init_calls.append("  initTable('device-events-table');")
    if show_device_enforcements:
        init_calls.append("  initTable('device-enforcement-table');")
    if show_device_recalls:
        init_calls.append("  initTable('device-recall-table');")
    if show_device_registrationlisting:
        init_calls.append("  initTable('device-reglist-table');")
    if show_transparency_crl:
        init_calls.append("  initTable('transparency-crl-table');")

    html_tpl = """<!doctype html>
<html>
  <head>
  <meta charset="utf-8">
  <title>IND __COMPANY__</title>
  <link rel="icon" type="image/svg+xml" href="__ICON_HREF__">
<style>
:root { font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; }
body { margin:0; background:#0b1220; color:#e6edf3; }
header { padding:16px 24px; border-bottom:1px solid #1f2a44; position:sticky; top:0; background:#0b1220; }
.container { padding:24px; display:grid; gap:16px; }
.card { background:#0f172a; border:1px solid #1f2a44; border-radius:14px; padding:16px; }
.title { font-size:20px; margin:0 0 8px; }
table { width:100%; border-collapse: collapse; }
th, td { text-align:left; border-bottom:1px solid #1f2a44; padding:8px; }
th { font-weight:600; }
th[data-sort] { cursor: pointer; user-select: none; }
th[data-sort]::after { content: ' ↕'; font-weight: 400; color: #a4b1c6; }
th.sorted-asc::after { content: ' ↑'; }
th.sorted-desc::after { content: ' ↓'; }
tr.filters th { padding-top: 6px; padding-bottom: 10px; }
tr.filters select {
  width: 100%;
  background: #0b1220;
  color: #e6edf3;
  border: 1px solid #1f2a44;
  border-radius: 10px;
  padding: 6px 8px;
}
</style></head>
<body>
<header><strong>IND __COMPANY__</strong></header>
<div class="container">
__DRUG_CARD____DEVICE_CARD____DEVICE_EVENT_CARD____NDC_CARD____ADVERSE_CARD____ENFORCEMENT_CARD____LABEL_CARD____SHORTAGES_CARD____DEVICE_ENFORCEMENT_CARD____DEVICE_RECALL_CARD____DEVICE_REGLIST_CARD____TRANSPARENCY_CRL_CARD__
</div>
<script>
(function() {
  function initTable(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const tbody = table.querySelector('tbody');
    const filterSelects = Array.from(table.querySelectorAll('select[data-filter]'));
    const headers = Array.from(table.querySelectorAll('th[data-sort]'));

    function getCellText(row, col) {
      const cell = row.querySelector(`td[data-col="${col}"]`);
      return cell ? (cell.textContent || '').trim() : '';
    }

    function uniqueSorted(values) {
      const set = new Set(values.filter(v => v !== ''));
      return Array.from(set).sort((a,b) => a.localeCompare(b, undefined, {numeric:true, sensitivity:'base'}));
    }

    function getActiveFilters(uptoIndexExclusive) {
      const active = {};
      filterSelects.forEach((sel, idx) => {
        if (idx >= uptoIndexExclusive) return;
        const col = sel.getAttribute('data-filter');
        const val = (sel.value || '').trim();
        if (val !== '') active[col] = val;
      });
      return active;
    }

    function rowMatchesActive(row, active) {
      for (const [col, val] of Object.entries(active)) {
        if (getCellText(row, col) !== val) return false;
      }
      return true;
    }

    function applyFilters() {
      const active = {};
      filterSelects.forEach(sel => {
        const col = sel.getAttribute('data-filter');
        const val = (sel.value || '').trim();
        if (val !== '') active[col] = val;
      });

      const rows = Array.from(tbody.querySelectorAll('tr'));
      rows.forEach(row => {
        if (row.children.length === 1 && row.textContent.includes('(none)')) {
          row.style.display = '';
          return;
        }
        row.style.display = rowMatchesActive(row, active) ? '' : 'none';
      });
    }

    function updateCascadingFilters() {
      const allRows = Array.from(tbody.querySelectorAll('tr'));
      const dataRows = allRows.filter(r => !(r.children.length === 1 && r.textContent.includes('(none)')));

      filterSelects.forEach((sel, idx) => {
        const col = sel.getAttribute('data-filter');
        const prevActive = getActiveFilters(idx);
        const eligibleRows = dataRows.filter(r => rowMatchesActive(r, prevActive));
        const vals = eligibleRows.map(r => getCellText(r, col));
        const uniques = uniqueSorted(vals);

        const current = (sel.value || '').trim();
        while (sel.options.length > 1) sel.remove(1);
        uniques.forEach(v => {
          const opt = document.createElement('option');
          opt.value = v;
          opt.textContent = v;
          sel.appendChild(opt);
        });

        if (current !== '' && !uniques.includes(current)) {
          sel.value = '';
        } else {
          sel.value = current;
        }
      });

      applyFilters();
    }

    filterSelects.forEach(sel => {
      sel.addEventListener('change', () => {
        updateCascadingFilters();
      });
    });

    let sortState = { col: null, dir: 'asc' };

    function clearHeaderIndicators() {
      headers.forEach(h => h.classList.remove('sorted-asc', 'sorted-desc'));
    }

    function sortRows(col, dir) {
      const rows = Array.from(tbody.querySelectorAll('tr'))
        .filter(r => !(r.children.length === 1 && r.textContent.includes('(none)')));

      rows.sort((ra, rb) => {
        const a = getCellText(ra, col);
        const b = getCellText(rb, col);
        const cmp = a.localeCompare(b, undefined, {numeric:true, sensitivity:'base'});
        return dir === 'asc' ? cmp : -cmp;
      });

      rows.forEach(r => tbody.appendChild(r));
    }

    headers.forEach(h => {
      h.addEventListener('click', () => {
        const col = h.getAttribute('data-sort');
        if (!col) return;

        const nextDir = (sortState.col === col && sortState.dir === 'asc') ? 'desc' : 'asc';
        sortState = { col, dir: nextDir };

        clearHeaderIndicators();
        h.classList.add(nextDir === 'asc' ? 'sorted-asc' : 'sorted-desc');

        sortRows(col, nextDir);
        updateCascadingFilters();
      });
    });

    updateCascadingFilters();
  }

__INIT_CALLS__
})();
</script>
</body></html>
"""

    return (
        html_tpl
        .replace("__COMPANY__", company_esc)
        .replace("__ICON_HREF__", esc(icon_href))
        .replace("__DRUG_CARD__", drug_card if show_drug_approved else "")
        .replace("__NDC_CARD__", ndc_card if show_drug_ndc else "")
        .replace("__ADVERSE_CARD__", adverse_card if show_drug_adverse_events else "")
        .replace("__ENFORCEMENT_CARD__", enforcement_card if show_drug_enforcements else "")
        .replace("__LABEL_CARD__", label_card if show_drug_labels else "")
        .replace("__SHORTAGES_CARD__", shortages_card if show_drug_shortages else "")
        .replace("__DEVICE_CARD__", device_card if show_device_approved else "")
        .replace("__DEVICE_EVENT_CARD__", device_event_card if show_device_adverse_events else "")
        .replace("__DEVICE_ENFORCEMENT_CARD__", device_enforcement_card if show_device_enforcements else "")
        .replace("__DEVICE_RECALL_CARD__", device_recall_card if show_device_recalls else "")
        .replace("__DEVICE_REGLIST_CARD__", device_reglist_card if show_device_registrationlisting else "")
        .replace("__TRANSPARENCY_CRL_CARD__", transparency_crl_card if show_transparency_crl else "")
        .replace("__DRUGS_ROWS__", drugs_rows)
        .replace("__NDC_ROWS__", ndc_rows)
        .replace("__ADVERSE_ROWS__", adverse_rows)
        .replace("__ENFORCEMENT_ROWS__", enforcement_rows)
        .replace("__LABEL_ROWS__", label_rows)
        .replace("__SHORTAGES_ROWS__", shortages_rows)
        .replace("__DEVICES_ROWS__", devices_rows)
        .replace("__DEVICE_EVENT_ROWS__", device_event_rows)
        .replace("__DEVICE_ENFORCEMENT_ROWS__", device_enforcement_rows)
        .replace("__DEVICE_RECALL_ROWS__", device_recall_rows)
        .replace("__DEVICE_REGLIST_ROWS__", device_reglist_rows)
        .replace("__TRANSPARENCY_CRL_ROWS__", transparency_crl_rows)
        .replace("__INIT_CALLS__", "\n".join(init_calls))
    )